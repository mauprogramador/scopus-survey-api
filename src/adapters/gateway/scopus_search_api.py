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

    __PAGE_TWO_INDEX = 1
    __START = 1

    def __init__(
        self,
        http_client: HTTPClient,
        url_builder: URLBuilder,
        survey_detail: SurveyDetail,
    ) -> None:
        """Search and retrieve articles via the Scopus Search API"""
        self.__http_client = http_client
        self.__url_builder = url_builder
        self.__survey_detail = survey_detail
        self.__search: ScopusSearch = None

        try:
            self.__workers = min(2 * len(sched_getaffinity(0)), 32)
        except AttributeError:
            self.__workers = min(2 * (cpu_count() or 4), 32)

    async def __task_request(
        self, url: str, index: int
    ) -> tuple[int, ResponseBundle]:
        response = await self.__http_client.request(url)
        return index, response

    async def survey_totals_found(
        self, bundles_map: dict[int, CombinationBundle]
    ) -> list[Json]:
        max_workers = min(len(bundles_map), self.__workers)
        LOG.debug({"max_workers": max_workers})

        all_tasks = {
            create_task(
                self.__task_request(bundle.url, index),
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

                    await self.__http_client.close()

                    if isinstance(exc, HTTPError):
                        raise exc

                    raise ServiceUnavailable(CANCELLED_ERROR, exc) from exc

        if remaining_tasks:
            await gather(*remaining_tasks, return_exceptions=True)

        await self.__http_client.close()
        self.__survey_detail.set_quota_data(last_completed)

        return [bundle.model_dump() for bundle in bundles_map.values()]

    async def __get_by_pagination(self, index: int) -> ResponseBundle:
        page = index * self.__search.items_per_page
        url = self.__url_builder.pagination_url(page)
        return await self.__http_client.request(url)

    async def __get_multiple_articles_by_pagination(self) -> None:
        pages_count = self.__search.pages_count
        max_workers = min((pages_count - self.__START), self.__workers)
        LOG.debug({"max_workers": max_workers})

        all_tasks = {
            create_task(
                self.__get_by_pagination(start),
                name=f"pagination_start:{start}",
            )
            for start in range(self.__START, pages_count)
        }
        remaining_tasks = all_tasks.copy()

        total = self.__search.total_results
        step = self.__search.items_per_page

        with (
            ThreadPoolExecutor(max_workers) as executor,
            ProgressBar(total, step, self.__START) as progress_bar,
        ):
            for future in as_completed(all_tasks):
                remaining_tasks.discard(future)

                try:
                    response = await future
                    search = await get_running_loop().run_in_executor(
                        executor,
                        ScopusResponse.validate_search,
                        response,
                    )
                    self.__search.entry.extend(search.entry)
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

    async def search_articles(self, params: SearchParams) -> list[ScopusEntry]:
        url = self.__url_builder.search_url(params)

        try:
            response = await self.__http_client.request(url)
            self.__search = ScopusResponse.validate_search(response)

            self.__survey_detail.set_search_data(self.__search)
            # self.__search.set_count_limit(params.max_count)

            if self.__search.total_results == 0:
                raise NotFound(ARTICLES_NOT_FOUND)

            if self.__search.pages_count == 2:
                response = await self.__get_by_pagination(
                    self.__PAGE_TWO_INDEX
                )

                search = ScopusResponse.validate_search(response)
                self.__search.entry.extend(search.entry)

            elif self.__search.pages_count > 2:
                await self.__get_multiple_articles_by_pagination()

            LOG.info(
                "Total Articles Found: "
                f"\033[33;1m{self.__search.total_results}"
            )

        finally:
            await self.__http_client.close()

        return self.__search.entry
