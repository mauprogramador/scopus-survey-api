from asyncio import (
    CancelledError,
    as_completed,
    create_task,
    gather,
    get_running_loop,
)
from concurrent.futures import ThreadPoolExecutor
from os import cpu_count, sched_getaffinity

from src.adapters.helpers.scopus_response import ScopusResponse
from src.core.common.error_messages import CANCELLED_ERROR
from src.core.common.types import (
    CombinationBundle,
    Json,
    ResponseBundle,
    SearchParams,
)
from src.core.config.config import LOG
from src.core.domain.http_exceptions import (
    HTTPError,
    ServiceUnavailable,
)
from src.core.domain.protocols import (
    HTTPClient,
    QuotaResultsHandler,
    SurveyDetails,
    URLBuilder,
)
from src.utils.progress_bar import ProgressBar


class ScopusSearchAPI:
    """Search and retrieve articles via the Scopus Search API"""

    _PAGE_TWO_INDEX = 1

    def __init__(
        self,
        http_client: HTTPClient,
        url_builder: URLBuilder,
        survey_details: SurveyDetails,
        state: QuotaResultsHandler,
    ) -> None:
        """Search and retrieve articles via the Scopus Search API"""
        self._http_client = http_client
        self._url_builder = url_builder
        self._details = survey_details
        self._state = state

        try:
            self._workers = min(2 * len(sched_getaffinity(0)), 32)
        except AttributeError:
            self._workers = min(2 * (cpu_count() or 4), 32)

    @property
    def http_client(self) -> HTTPClient:
        return self._http_client

    async def _task_request(
        self, url: str, index: int
    ) -> tuple[int, ResponseBundle]:
        response = await self._http_client.request(url)
        return index, response

    async def survey_totals_found(
        self, bundles_map: dict[int, CombinationBundle]
    ) -> list[Json]:
        max_workers = min(len(bundles_map), self._workers)
        LOG.debug({"max_workers": max_workers})

        all_tasks = {
            create_task(
                self._task_request(bundle.url, index),
                name=f"combination_index:{index}",
            )
            for index, bundle in bundles_map.items()
        }
        remaining_tasks = all_tasks.copy()
        last_completed: ResponseBundle = None

        with (
            ThreadPoolExecutor(max_workers) as executor,
            ProgressBar.start(len(bundles_map)) as progress,
        ):
            for future in as_completed(all_tasks):
                remaining_tasks.discard(future)

                try:
                    index, response = await future
                    last_completed = response

                    search = await get_running_loop().run_in_executor(
                        executor,
                        ScopusResponse.validate_search,
                        response,
                    )
                    bundles_map[index].total = search.total_results
                    progress.step()

                except (CancelledError, HTTPError, Exception) as exc:

                    for task in remaining_tasks:
                        if task.done() and not isinstance(exc, CancelledError):
                            task.exception()  # Retrieve task exception
                        else:
                            task.cancel()

                    await self._http_client.close()

                    if isinstance(exc, HTTPError):
                        raise exc

                    raise ServiceUnavailable(CANCELLED_ERROR, exc) from exc

        if remaining_tasks:
            await gather(*remaining_tasks, return_exceptions=True)

        await self._http_client.close()
        self._details.set_search_quota(last_completed)

        return [bundle.model_dump() for bundle in bundles_map.values()]

    async def _get_by_pagination(self, index: int) -> ResponseBundle:
        page = index * self._state.items_per_page
        url = self._url_builder.pagination_url(page)
        return await self._http_client.request(url)

    async def _get_multiple_articles_by_pagination(self) -> None:
        max_workers = min(self._state.pages_to_fetch, self._workers)
        LOG.debug({"max_workers": max_workers})

        all_tasks = {
            create_task(
                self._get_by_pagination(start),
                name=f"pagination_start:{start}",
            )
            for start in self._state.pages_to_fetch_range
        }
        remaining_tasks = all_tasks.copy()
        last_completed: ResponseBundle = None
        progress_args = self._state.pages_to_fetch_progress

        with (
            ThreadPoolExecutor(max_workers) as executor,
            ProgressBar.start(*progress_args) as progress,
        ):
            for future in as_completed(all_tasks):
                remaining_tasks.discard(future)

                try:
                    response = await future
                    last_completed = response

                    search = await get_running_loop().run_in_executor(
                        executor,
                        ScopusResponse.validate_search,
                        response,
                    )
                    self._state.entry.extend(search.entry)
                    progress.step()

                except (CancelledError, HTTPError, Exception) as exc:

                    for task in remaining_tasks:
                        if task.done() and not isinstance(exc, CancelledError):
                            task.exception()  # Retrieve task exception
                        else:
                            task.cancel()

                    if isinstance(exc, HTTPError):
                        raise exc

                    raise ServiceUnavailable(CANCELLED_ERROR, exc) from exc

        if remaining_tasks:
            await gather(*remaining_tasks, return_exceptions=True)

        self._details.set_search_quota(last_completed)

    async def search_articles(self, params: SearchParams) -> None:
        url = self._url_builder.search_url(params)

        response = await self._http_client.request(url)
        search_results = ScopusResponse.validate_search(response)

        self._details.set_search_data(search_results)
        self._details.set_search_quota(response)

        self._state.set_first_search(search_results)

        if self._state.pages_count > 1:
            self._state.handle_search_quota(self._details.search_quota)

            if self._state.pages_count == 2:
                response = await self._get_by_pagination(self._PAGE_TWO_INDEX)
                self._details.set_search_quota(response)

                search_results = ScopusResponse.validate_search(response)
                self._state.entry.extend(search_results.entry)

            elif self._state.pages_count > 2:
                await self._http_client.update_strategy(
                    self._state.total_results
                )
                await self._get_multiple_articles_by_pagination()

        LOG.info(f"Total Found: \033[33m{self._state.total_results}")

        self._state.validate_integrity()
