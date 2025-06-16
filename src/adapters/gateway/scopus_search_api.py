from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm.contrib.logging import logging_redirect_tqdm

from src.core.common.messages import ARTICLES_NOT_FOUND, INTERRUPT_ERROR
from src.core.common.types import SearchParams
from src.core.config.config import LOG
from src.core.config.scopus import SCOPUS_HEADERS
from src.core.data.query_params import CombinationParams
from src.core.data.serializers import ScopusEntry, ScopusSearch
from src.core.data.survey_detail import SurveyDetail
from src.core.domain.http_exceptions import NotFound
from src.core.domain.interfaces import (
    HTTPClientABC,
    ScopusResponseABC,
    SearchAPIABC,
    URLBuilderABC,
)
from src.utils.progress_bar import ProgressBar


class ScopusSearchAPI(SearchAPIABC):
    """Search and retrieve articles via the Scopus Search API"""

    __PAGE_TWO_INDEX = 1
    __RATE_LIMIT = 9
    __START = 1

    def __init__(
        self,
        http_retry: HTTPClientABC,
        url_builder: URLBuilderABC,
        scopus_response: ScopusResponseABC,
        survey_detail: SurveyDetail,
    ) -> None:
        """Search and retrieve articles via the Scopus Search API"""
        self.__http_retry = http_retry
        self.__url_builder = url_builder
        self.__scopus_response = scopus_response
        self.__survey_detail = survey_detail
        self.__search_response: ScopusSearch = None

    async def search_articles(self, params: SearchParams) -> list[ScopusEntry]:
        url = self.__url_builder.search_url(params)

        try:
            self.__search_response = self.__get_search_response(url)
            self.__survey_detail.set_scopus_search(self.__search_response)
            self.__search_response.count_limit(params.max_count)

            if self.__search_response.total_results == 0:
                raise NotFound(ARTICLES_NOT_FOUND)

            if self.__search_response.pages_count == 2:
                self.__get_articles_by_pagination(self.__PAGE_TWO_INDEX)

            elif self.__search_response.pages_count > 2:
                self.__get_multiple_articles_by_pagination()

            LOG.info(
                "Total Articles Found: "
                f"\033[33;1m{self.__search_response.total_results}"
            )

        finally:
            await self.__http_retry.close()

        return self.__search_response.entry

    # def survey_results(
    #     self, params: CombinationParams, arrangements: list[str]
    # ) -> list[ScopusEntry]:
    #     url = self.__url_builder.set_survey_params(params)
    #     self.__http_retry.mount_session(SCOPUS_HEADERS)

    #     try:
    #         self.__search_response = self.__get_search_response(url)

    #         self.__get_multiple_articles_by_pagination()

    #     finally:
    #         self.__http_retry.close()

    #     return self.__search_response.entry

    def __get_search_response(self, url: str) -> ScopusSearch:
        response = self.__http_retry.request(url)
        search: ScopusSearch = self.__scopus_response.validate(response)

        return search

    def __get_articles_by_pagination(self, index: int) -> None:
        page = index * self.__search_response.items_per_page
        url = self.__url_builder.pagination_url(page)

        search_response = self.__get_search_response(url)
        self.__search_response.entry.extend(search_response.entry)

    def __get_multiple_articles_by_pagination(self) -> None:
        pages_count = self.__search_response.pages_count
        max_workers = min(pages_count, self.__RATE_LIMIT)

        LOG.debug({"max_workers": max_workers})
        progress_bar = ProgressBar(
            self.__search_response.total_results,
            self.__search_response.items_per_page,
            self.__START,
        )

        try:
            with (
                ThreadPoolExecutor(max_workers) as executor,
                logging_redirect_tqdm(LOG.logger),
            ):
                futures = [
                    executor.submit(self.__get_articles_by_pagination, index)
                    for index in range(self.__START, pages_count)
                ]
                for future in as_completed(futures):
                    future.result()
                    progress_bar.step()

                executor.shutdown(wait=True, cancel_futures=True)
                progress_bar.close()

        except (KeyboardInterrupt, Exception) as exc:
            executor.shutdown(wait=True, cancel_futures=True)
            progress_bar.close()

            if isinstance(exc, KeyboardInterrupt):
                LOG.info("\033[33mSignal received. Exiting gracefully")
                LOG.error(INTERRUPT_ERROR)

            raise exc
