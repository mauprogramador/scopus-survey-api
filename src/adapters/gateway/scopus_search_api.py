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
from src.core.data.serializers import ScopusEntry, ScopusSearch
from src.core.domain.http_exceptions import (
    HTTPError,
    NotFound,
    ServiceUnavailable,
)
from src.core.domain.protocols import HTTPClient, SurveyDetail, URLBuilder
from src.utils.progress_bar import ProgressBar


class ScopusSearchAPI:
    """Search and retrieve articles via the Scopus Search API"""

    _PAGE_TWO_INDEX = 1
    _START = 1

    def __init__(
        self,
        http_client: HTTPClient,
        url_builder: URLBuilder,
        survey_detail: SurveyDetail,
    ) -> None:
        """Search and retrieve articles via the Scopus Search API"""
        self._http_client = http_client
        self._url_builder = url_builder
        self._survey_detail = survey_detail
        self._search: ScopusSearch = None

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
            ProgressBar(len(bundles_map)) as progress_bar,
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
                    progress_bar.step()

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
        self._survey_detail.set_search_quota(last_completed)

        return [bundle.model_dump() for bundle in bundles_map.values()]

    async def _get_by_pagination(self, index: int) -> ResponseBundle:
        page = index * self._search.items_per_page
        url = self._url_builder.pagination_url(page)
        return await self._http_client.request(url)

    async def _get_multiple_articles_by_pagination(self) -> None:
        pages_count = self._search.pages_count
        max_workers = min((pages_count - self._START), self._workers)
        LOG.debug({"max_workers": max_workers})

        all_tasks = {
            create_task(
                self._get_by_pagination(start),
                name=f"pagination_start:{start}",
            )
            for start in range(self._START, pages_count)
        }
        remaining_tasks = all_tasks.copy()
        last_completed: ResponseBundle = None

        total = self._search.total_results
        step = self._search.items_per_page

        with (
            ThreadPoolExecutor(max_workers) as executor,
            ProgressBar(total, step, self._START) as progress_bar,
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
                    self._search.entry.extend(search.entry)
                    progress_bar.step()

                except (CancelledError, HTTPError, Exception) as exc:

                    for task in remaining_tasks:
                        if not task.done():
                            task.cancel()

                    if isinstance(exc, HTTPError):
                        raise exc

                    raise ServiceUnavailable(CANCELLED_ERROR, exc) from exc

        if remaining_tasks:
            await gather(*remaining_tasks, return_exceptions=True)

        self._survey_detail.set_search_quota(last_completed)

    async def search_articles(self, params: SearchParams) -> list[ScopusEntry]:
        url = self._url_builder.search_url(params)

        try:
            response = await self._http_client.request(url)
            self._search = ScopusResponse.validate_search(response)
            self._survey_detail.set_search_data(self._search)

            if self._search.total_results == 0:
                self._survey_detail.set_search_quota(response)
                raise NotFound(ARTICLES_NOT_FOUND)

            if self._search.pages_count == 2:
                response = await self._get_by_pagination(self._PAGE_TWO_INDEX)
                self._survey_detail.set_search_quota(response)

                search = ScopusResponse.validate_search(response)
                self._search.entry.extend(search.entry)

            elif self._search.pages_count > 2:
                await self._http_client.update_strategy(
                    self._search.pages_count
                )
                await self._get_multiple_articles_by_pagination()

            LOG.info("Total Found: " f"\033[33m{self._search.total_results}")

        finally:
            await self._http_client.close()

        return self._search.entry
