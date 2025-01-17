from concurrent.futures import ThreadPoolExecutor, as_completed

from pandas import DataFrame
from tqdm.contrib.logging import logging_redirect_tqdm

from app.core.config.config import SHUTDOWN, LOG
from app.core.config.scopus import SCOPUS_HEADERS
from app.core.data.serializers import ScopusAbstract, ScopusResult
from app.core.domain.exceptions import InterruptError
from app.core.domain.interfaces import (
    AbstractAPIABC,
    HTTPRetryABC,
    ScopusResponseABC,
    URLBuilderABC,
)
from app.utils.progress_bar import ProgressBar


class ScopusAbstractRetrievalAPI(AbstractAPIABC):
    """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""

    __ONE_RESULT_INDEX = 0
    __RATE_LIMIT = 9

    def __init__(
        self,
        http_retry: HTTPRetryABC,
        url_builder: URLBuilderABC,
        scopus_response: ScopusResponseABC,
    ) -> None:
        """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""
        self.__http_retry = http_retry
        self.__url_builder = url_builder
        self.__scopus_response = scopus_response
        self.__entry: list[ScopusResult] = None
        self.__abstracts: list[dict] = None
        self.__total = 0

    def retrieve_abstracts(
        self, api_key: str, entry: list[ScopusResult]
    ) -> DataFrame:
        self.__entry, self.__total = entry, len(entry)
        self.__abstracts = []

        self.__url_builder.set_abstract_api_key(api_key)
        self.__http_retry.mount_session(SCOPUS_HEADERS)

        try:
            if self.__total == 1:
                self.__get_abstract(self.__ONE_RESULT_INDEX)
            else:
                self.__get_multiple_abstracts()
        finally:
            self.__http_retry.close()

        return DataFrame(self.__abstracts)

    def __get_abstract(self, index: int) -> None:
        if SHUTDOWN.event.is_set():
            raise InterruptError()

        url = self.__url_builder.abstract_url(self.__entry[index].url)
        abstract = self.__get_abstract_response(url)
        self.__abstracts.append(abstract.model_dump(by_alias=True))

    def __get_abstract_response(self, url: str) -> ScopusAbstract:
        response = self.__http_retry.request(url)
        abstract: ScopusAbstract = self.__scopus_response.handle(response)

        return abstract

    def __get_multiple_abstracts(self) -> None:
        max_workers = min(self.__total, self.__RATE_LIMIT)

        LOG.debug({"max_workers": max_workers})
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
