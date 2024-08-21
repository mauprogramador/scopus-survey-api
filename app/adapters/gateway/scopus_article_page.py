from concurrent.futures import ThreadPoolExecutor, as_completed
from os import sched_getaffinity

from pandas import DataFrame, Series
from tqdm.contrib.logging import logging_redirect_tqdm

from app.core.config.config import HANDLER, LOG
from app.core.config.scopus import (
    NULL,
    SCOPUS_ID_COLUMN,
    SCRAPING_HEADERS,
    TEMPLATE_COLUMN,
    URL_COLUMN,
)
from app.core.domain.exceptions import InterruptError
from app.core.domain.metaclasses import ArticlesPage, HttpRetry, UrlBuilder
from app.framework.exceptions import BadGateway, GatewayTimeout
from app.utils.progress_bar import ProgressBar


class ScopusArticlesPage(ArticlesPage):
    """Retrieves Scopus articles preview pages via HTTP requests"""

    __ONE_ROW_INDEX = 0
    __PID = 0

    def __init__(self, http_helper: HttpRetry, url_helper: UrlBuilder) -> None:
        """Retrieves Scopus articles preview pages via HTTP requests"""
        self.__http_helper = http_helper
        self.__url_helper = url_helper
        self.__dataframe: DataFrame = None
        self.__total_rows = 0

    def get_articles_page(self, subset: DataFrame) -> DataFrame:
        self.__dataframe = subset
        self.__dataframe.loc[:, TEMPLATE_COLUMN] = Series()

        self.__http_helper.mount_session(SCRAPING_HEADERS)
        self.__total_rows = self.__dataframe.shape[0]

        try:
            if self.__total_rows == 1:
                self.__get_article_page_and_url(self.__ONE_ROW_INDEX)
            else:
                self.__get_multiple_article_pages_and_urls()
        finally:
            self.__http_helper.close()

        return self.__dataframe

    def __get_article_page_and_url(self, index: int) -> None:
        if HANDLER.event.is_set():
            raise InterruptError()

        scopus_id = self.__dataframe.loc[index, SCOPUS_ID_COLUMN]
        url = self.__url_helper.get_article_page_url(scopus_id)

        page = self.__get_article_preview_page(url)

        if page == NULL:
            LOG.info('Retrying article page...')
            page = self.__get_article_preview_page(url)

        self.__dataframe.loc[index, URL_COLUMN] = url
        self.__dataframe.loc[index, TEMPLATE_COLUMN] = page

    def __get_article_preview_page(self, url: str) -> str:
        try:
            response = self.__http_helper.request(url)

            if response.status_code != 200 or not response.text:
                LOG.error("Invalid response from article page")
                return NULL

        except (BadGateway, GatewayTimeout) as error:
            LOG.error("Invalid response from article page")
            LOG.error(repr(error))
            return NULL

        return response.text

    def __get_multiple_article_pages_and_urls(self) -> None:
        cpu_count = len(sched_getaffinity(self.__PID))
        max_workers = min(self.__total_rows, cpu_count)

        LOG.debug({"max_workers": max_workers})
        LOG.info("Getting Multiple Article Pages and URLs")
        progress_bar = ProgressBar(self.__total_rows)

        with (
            ThreadPoolExecutor(max_workers) as executor,
            logging_redirect_tqdm(LOG.logger),
        ):
            futures = [
                executor.submit(self.__get_article_page_and_url, index)
                for index in range(self.__total_rows)
            ]
            for future in as_completed(futures):
                future.result()
                progress_bar.step_progress()

            executor.shutdown(True, cancel_futures=True)
            progress_bar.close()
