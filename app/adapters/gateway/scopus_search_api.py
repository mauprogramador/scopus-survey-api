from concurrent.futures import ThreadPoolExecutor, as_completed
from json.decoder import JSONDecodeError
from os import sched_getaffinity

from pandas import DataFrame
from tqdm.contrib.logging import logging_redirect_tqdm

from app.core.common.messages import (
    DECODING_ERROR,
    NOT_FOUND_ERROR,
    SCOPUS_API_ERROR,
    VALIDATE_ERROR,
)
from app.core.common.types import SearchParams
from app.core.config.config import HANDLER, LOG
from app.core.config.scopus import LINK_LOG, QUOTA_LOG, get_search_headers
from app.core.data.serializers import ScopusJsonSchema, ScopusHeaders
from app.core.domain.exceptions import InterruptError, ScopusAPIError
from app.core.domain.metaclasses import HttpRetry, SearchAPI, UrlBuilder
from app.framework.exceptions import BadGateway, InternalError, NotFound
from app.utils.progress_bar import ProgressBar


class ScopusSearchAPI(SearchAPI):
    """Search and retrieve articles via the Scopus Search API"""

    __PAGE_TWO_INDEX = 1
    __PID = 0
    __START = 1

    def __init__(
        self, http_helper: HttpRetry, url_builder: UrlBuilder
    ) -> None:
        """Search and retrieve articles via the Scopus Search API"""
        self.__http_helper = http_helper
        self.__url_builder = url_builder
        self.__scopus_response: ScopusJsonSchema = None

    def search_articles(self, search_params: SearchParams) -> DataFrame:
        headers = get_search_headers(search_params.api_key)
        url = self.__url_builder.get_search_url(search_params.keywords)

        self.__http_helper.mount_session(headers)
        try:
            scopus_response = self.__get_scopus_response(url)
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

        return DataFrame(self.__scopus_response.articles)

    def __get_scopus_response(self, url: str) -> ScopusJsonSchema:
        response = self.__http_helper.request(url)

        if response.status_code == 429:
            headers = ScopusHeaders.model_validate(response.headers)
            if headers.quota_exceeded:
                LOG.error(QUOTA_LOG.format(headers.reset_datetime), False)
                LOG.info(LINK_LOG)

        if response.status_code != 200:
            raise ScopusAPIError(response)

        if not response.text:
            raise BadGateway(SCOPUS_API_ERROR)

        try:
            LOG.debug(response.json())

            return ScopusJsonSchema.model_validate(response.json())

        except JSONDecodeError as error:
            raise InternalError(DECODING_ERROR) from error

        except KeyError as error:
            raise InternalError(VALIDATE_ERROR) from error

    def __get_articles_by_pagination(self, index: int) -> None:
        if HANDLER.event.is_set():
            raise InterruptError()

        page = index * self.__scopus_response.items_per_page
        url = self.__url_builder.get_pagination_url(page)

        scopus_response = self.__get_scopus_response(url)
        self.__scopus_response.entry.extend(scopus_response.entry)

    def __get_multiple_articles_by_pagination(self) -> None:
        pages_count = self.__scopus_response.pages_count

        cpu_count = len(sched_getaffinity(self.__PID))
        max_workers = min(pages_count, cpu_count)

        LOG.debug({"max_workers": max_workers})
        LOG.info("Getting Multiple Articles by Pagination")
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
