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
from src.core.common.error_messages import ARTICLES_NOT_FOUND, CANCELLED_ERROR
from src.core.common.types import (
    CombinationBundle,
    Json,
    ResponseBundle,
    SearchParams,
)
from src.core.config.config import LOG
from src.core.data.quota_results_handler import QuotaResultsHandler
from src.core.domain.http_exceptions import (
    HTTPError,
    NotFound,
    ServiceUnavailable,
)
from src.core.domain.protocols import HTTPClient, SurveyDetails, URLBuilder
from src.utils.progress_bar import ProgressBar


class ScopusSearchAPI:
    """Search and retrieve articles via the Scopus Search API"""

    _PAGE_TWO_INDEX = 1
    _FIRST_SEARCH = 1

    def __init__(
        self,
        http_client: HTTPClient,
        url_builder: URLBuilder,
        survey_details: SurveyDetails,
    ) -> None:
        """Search and retrieve articles via the Scopus Search API"""
        self._http_client = http_client
        self._url_builder = url_builder
        self._details = survey_details
        self._state: QuotaResultsHandler = None

        try:
            self._workers = min(2 * len(sched_getaffinity(0)), 32)
        except AttributeError:
            self._workers = min(2 * (cpu_count() or 4), 32)

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
                        if not task.done():
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
        pages_count = self._state.pages_count
        max_workers = min((pages_count - self._FIRST_SEARCH), self._workers)
        LOG.debug({"max_workers": max_workers})

        all_tasks = {
            create_task(
                self._get_by_pagination(start),
                name=f"pagination_start:{start}",
            )
            for start in range(self._FIRST_SEARCH, pages_count)
        }
        remaining_tasks = all_tasks.copy()
        last_completed: ResponseBundle = None

        total = self._state.total_results
        step = self._state.items_per_page

        with (
            ThreadPoolExecutor(max_workers) as executor,
            ProgressBar.start(total, step, self._FIRST_SEARCH) as progress,
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
                        if not task.done():
                            task.cancel()

                    if isinstance(exc, HTTPError):
                        raise exc

                    raise ServiceUnavailable(CANCELLED_ERROR, exc) from exc

        if remaining_tasks:
            await gather(*remaining_tasks, return_exceptions=True)

        self._details.set_search_quota(last_completed)

    async def search_articles(
        self, params: SearchParams
    ) -> QuotaResultsHandler:
        url = self._url_builder.search_url(params)

        try:
            response = await self._http_client.request(url)
            search_results = ScopusResponse.validate_search(response)
            self._details.set_search_data(search_results)
            self._details.set_search_quota(response)

            self._results = QuotaResultsHandler(search_results)

            if self._results.total_results == 0:
                raise NotFound(ARTICLES_NOT_FOUND)

            if self._state.pages_count > 1:
                self._state.handle_search_quota(self._details.search_quota)

                if self._state.pages_count == 2:
                    response = await self._get_by_pagination(
                        self._PAGE_TWO_INDEX
                    )
                    self._details.set_search_quota(response)

                    search_results = ScopusResponse.validate_search(response)
                    self._state.entry.extend(search_results.entry)

                elif self._state.pages_count > 2:
                    await self._http_client.update_strategy(
                        self._state.total_results
                    )
                    await self._get_multiple_articles_by_pagination()

            LOG.info(f"Total Found: \033[33m{self._state.total_results}")

        finally:
            await self._http_client.close()

        return self._state
