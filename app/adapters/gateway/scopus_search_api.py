from concurrent.futures import ThreadPoolExecutor, as_completed
from json.decoder import JSONDecodeError

from tqdm.contrib.logging import logging_redirect_tqdm

from app.core.common.messages import (
    DECODING_ERROR,
    NOT_FOUND_ERROR,
    SEARCH_API_ERROR,
    VALIDATE_ERROR,
)
from app.core.config.config import HANDLER, LOG
from app.core.config.scopus import get_scopus_headers
from app.core.data.dtos import SearchParams
from app.core.data.serializers import ScopusResult, ScopusSearch
from app.core.domain.exceptions import InterruptError, ScopusAPIError
from app.core.domain.metaclasses import HTTPRetry, SearchAPI, URLBuilder
from app.framework.exceptions import BadGateway, InternalError, NotFound
from app.utils.progress_bar import ProgressBar


class ScopusSearchAPI(SearchAPI):
    """Search and retrieve articles via the Scopus Search API"""

    __PAGE_TWO_INDEX = 1
    __RATE_LIMIT = 9
    __START = 1

    def __init__(
        self, http_helper: HTTPRetry, url_builder: URLBuilder
    ) -> None:
        """Search and retrieve articles via the Scopus Search API"""
        self.__http_helper = http_helper
        self.__url_builder = url_builder
        self.__scopus_response: ScopusSearch = None

    def search_articles(
        self, search_params: SearchParams
    ) -> list[ScopusResult]:
        headers = get_scopus_headers(search_params.api_key)
        url = self.__url_builder.get_search_url(search_params.keywords)
        self.__http_helper.mount_session(headers)

        try:
            scopus_response = self.__get_search_response(url)
            self.__scopus_response = scopus_response

            if scopus_response.total_results == 0:
                raise NotFound(NOT_FOUND_ERROR)

            if scopus_response.pages_count == 2:
                self.__get_articles_by_pagination(self.__PAGE_TWO_INDEX)

            elif scopus_response.pages_count > 2:
                self.__get_multiple_articles_by_pagination()

            LOG.info(f"Total Articles Found: {scopus_response.total_results}")

        finally:
            self.__http_helper.close()

        return self.__scopus_response.entry

    def __get_search_response(self, url: str) -> ScopusSearch:
        response = self.__http_helper.request(url)

        if response.status_code != 200:
            raise ScopusAPIError(response, SEARCH_API_ERROR)

        if not response.text:
            raise BadGateway(SEARCH_API_ERROR)

        try:
            return ScopusSearch.model_validate(response.json())

        except JSONDecodeError as error:
            raise InternalError(DECODING_ERROR) from error

        except KeyError as error:
            raise InternalError(VALIDATE_ERROR) from error

    def __get_articles_by_pagination(self, index: int) -> None:
        if HANDLER.event.is_set():
            raise InterruptError()

        page = index * self.__scopus_response.items_per_page
        url = self.__url_builder.get_pagination_url(page)

        scopus_response = self.__get_search_response(url)
        self.__scopus_response.entry.extend(scopus_response.entry)

    def __get_multiple_articles_by_pagination(self) -> None:
        pages_count = self.__scopus_response.pages_count
        max_workers = min(pages_count, self.__RATE_LIMIT)

        LOG.debug({"max_workers": max_workers})
        LOG.info("Getting multiple articles by pagination")
        progress_bar = ProgressBar(
            self.__scopus_response.total_results,
            self.__scopus_response.items_per_page,
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
