from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm.contrib.logging import logging_redirect_tqdm

from app.core.common.messages import NOT_FOUND_ERROR
from app.core.config.config import SHUTDOWN, LOG
from app.core.config.scopus import SCOPUS_HEADERS
from app.core.data.query import SearchParams
from app.core.data.serializers import ScopusResult, ScopusSearch
from app.core.domain.exceptions import InterruptError
from app.core.domain.http_exceptions import NotFound
from app.core.domain.interfaces import (
    HTTPRetryABC,
    ScopusResponseABC,
    SearchAPIABC,
    URLBuilderABC,
)
from app.utils.progress_bar import ProgressBar


class ScopusSearchAPI(SearchAPIABC):
    """Search and retrieve articles via the Scopus Search API"""

    __PAGE_TWO_INDEX = 1
    __RATE_LIMIT = 9
    __START = 1

    def __init__(
        self,
        http_retry: HTTPRetryABC,
        url_builder: URLBuilderABC,
        scopus_response: ScopusResponseABC,
    ) -> None:
        """Search and retrieve articles via the Scopus Search API"""
        self.__http_retry = http_retry
        self.__url_builder = url_builder
        self.__scopus_response = scopus_response
        self.__search_response: ScopusSearch = None

    def search_articles(self, params: SearchParams) -> list[ScopusResult]:
        url = self.__url_builder.search_url(params)
        self.__http_retry.mount_session(SCOPUS_HEADERS)

        try:
            self.__search_response = self.__get_search_response(url)

            if self.__search_response.total_results == 0:
                raise NotFound(NOT_FOUND_ERROR)

            if self.__search_response.pages_count == 2:
                self.__get_articles_by_pagination(self.__PAGE_TWO_INDEX)

            elif self.__search_response.pages_count > 2:
                self.__get_multiple_articles_by_pagination()

            LOG.info(
                "Total Articles Found: "
                f"\033[33;1m{self.__search_response.total_results}"
            )

        finally:
            self.__http_retry.close()

        return self.__search_response.entry

    def __get_search_response(self, url: str) -> ScopusSearch:
        response = self.__http_retry.request(url)
        search: ScopusSearch = self.__scopus_response.handle(response)

        return search

    def __get_articles_by_pagination(self, index: int) -> None:
        if SHUTDOWN.event.is_set():
            raise InterruptError()

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
                progress_bar.step_progress()

            executor.shutdown(wait=True, cancel_futures=True)
            progress_bar.close()
