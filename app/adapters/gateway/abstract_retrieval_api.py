from concurrent.futures import ThreadPoolExecutor, as_completed
from json.decoder import JSONDecodeError
from os import sched_getaffinity

from pandas import DataFrame
from tqdm.contrib.logging import logging_redirect_tqdm

from app.core.common.messages import (
    ABSTRACT_API_ERROR,
    DECODING_ERROR,
    VALIDATE_ERROR,
)
from app.core.config.config import HANDLER, LOG
from app.core.config.scopus import (
    FURTHER_INFO_LINK,
    QUOTA_WARNING,
    get_scopus_headers,
)
from app.core.data.serializers import (
    ScopusArticle,
    ScopusHeaders,
    ScopusResult,
)
from app.core.domain.exceptions import InterruptError, ScopusAPIError
from app.core.domain.metaclasses import AbstractAPI, HTTPRetry, URLBuilder
from app.framework.exceptions import BadGateway
from app.framework.exceptions.http_exceptions import InternalError
from app.utils.progress_bar import ProgressBar


class AbstractRetrievalAPI(AbstractAPI):
    """Retrieves Scopus articles preview pages via HTTP requests"""

    __ONE_RESULT_INDEX = 0
    __RATIO = 90
    __PID = 0

    def __init__(self, http_helper: HTTPRetry, url_helper: URLBuilder) -> None:
        """Retrieves Scopus articles preview pages via HTTP requests"""
        self.__http_helper = http_helper
        self.__url_helper = url_helper
        self.__entry: list[ScopusResult] = None
        self.__abstracts: list[dict] = None
        self.__total = 0

    def retrieve_abstracts(
        self, api_key: str, entry: list[ScopusResult]
    ) -> DataFrame:
        self.__entry, self.__total = entry, len(entry)
        self.__abstracts = []

        headers = get_scopus_headers(api_key)
        self.__http_helper.mount_session(headers)

        try:
            if self.__total == 1:
                self.__get_abstract(self.__ONE_RESULT_INDEX)
            else:
                self.__get_multiple_abstracts()
        finally:
            self.__http_helper.close()

        return DataFrame(self.__abstracts)

    def __get_abstract(self, index: int) -> None:
        if HANDLER.event.is_set():
            raise InterruptError()

        url = self.__url_helper.get_abstract_url(self.__entry[index].url)
        abstract = self.__get_abstract_response(url)
        self.__abstracts.append(abstract.model_dump(by_alias=True))

    def __get_abstract_response(self, url: str) -> ScopusArticle:
        response = self.__http_helper.request(url)

        if response.status_code == 429:
            headers = ScopusHeaders.model_validate(response.headers)
            if headers.quota_exceeded >= self.__RATIO:
                LOG.error(QUOTA_WARNING.format(headers.reset_datetime))
                LOG.info(FURTHER_INFO_LINK)

        if response.status_code != 200:
            raise ScopusAPIError(response, ABSTRACT_API_ERROR)

        if not response.text:
            raise BadGateway(ABSTRACT_API_ERROR)

        try:
            return ScopusArticle.model_validate(response.json())

        except JSONDecodeError as error:
            raise InternalError(DECODING_ERROR) from error

        except KeyError as error:
            raise InternalError(VALIDATE_ERROR) from error

    def __get_multiple_abstracts(self) -> None:
        cpu_count = len(sched_getaffinity(self.__PID))
        max_workers = min(self.__total, cpu_count)

        LOG.debug({"max_workers": max_workers})
        LOG.info("Getting multiple article abstracts")
        progress_bar = ProgressBar(self.__total)

        with (
            ThreadPoolExecutor(max_workers) as executor,
            logging_redirect_tqdm(LOG.logger),
        ):
            futures = [
                executor.submit(self.__get_abstract, index)
                for index in range(self.__total)
            ]
            for future in as_completed(futures):
                future.result()
                progress_bar.step_progress()

            executor.shutdown(True, cancel_futures=True)
            progress_bar.close()
