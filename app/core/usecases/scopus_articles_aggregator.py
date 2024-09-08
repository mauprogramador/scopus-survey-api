from concurrent.futures import ProcessPoolExecutor, as_completed
from os import sched_getaffinity

from fastapi.responses import FileResponse
from pandas import DataFrame
from tqdm.contrib.logging import logging_redirect_tqdm

from app.core.common.types import SearchParams
from app.core.config.config import FILE_PATH, FILENAME, HEADERS, LOG
from app.core.config.scopus import (
    ABSTRACT_COLUMN,
    AUTHORS_COLUMN,
    COLUMNS_MAPPING,
    SCOPUS_ID_COLUMN,
    TITLE_COLUMN,
    URL_COLUMN,
)
from app.core.domain.metaclasses import (
    ArticlesAggregator,
    ArticlesScraper,
    SearchAPI,
    SimilarityFilter,
)
from app.utils.progress_bar import ProgressBar


class ScopusArticlesAggregator(ArticlesAggregator):
    """Gathers, filters and compiles data from Scopus articles"""

    __SCRAPE_COLUMNS = [URL_COLUMN, AUTHORS_COLUMN, ABSTRACT_COLUMN]
    __SUBSET_COLUMNS = [SCOPUS_ID_COLUMN, URL_COLUMN]
    __DROP_COLUMNS = [TITLE_COLUMN, AUTHORS_COLUMN]
    __MEDIA_TYPE = "text/csv"
    __LOCATIONS = (2, 5)
    __ONE_ROW_INDEX = 0
    __SEP = ";"
    __PID = 0

    def __init__(
        self,
        search_api: SearchAPI,
        articles_scraper: ArticlesScraper,
        similarity_filter: SimilarityFilter,
    ) -> None:
        """Gathers, filters and compiles data from Scopus articles"""
        self.__search_api = search_api
        self.__articles_scraper = articles_scraper
        self.__similarity_filter = similarity_filter
        self.__dataframe: DataFrame = None

    def get_articles(self, params: SearchParams) -> FileResponse:
        self.__dataframe = self.__search_api.search_articles(params)
        rows_before = self.__dataframe.shape[0]

        self.__dataframe = self.__dataframe.drop_duplicates()
        self.__dataframe = self.__dataframe.reset_index(drop=True)

        subset = self.__dataframe[self.__SUBSET_COLUMNS].copy()
        self.__articles_scraper.set_subset(subset)

        self.__dataframe.insert(self.__LOCATIONS[0], AUTHORS_COLUMN, None)
        self.__dataframe.insert(self.__LOCATIONS[1], ABSTRACT_COLUMN, None)

        if self.__dataframe.shape[0] > 1:
            self.__multiple_web_scraping()

        else:
            scrape_data = self.__articles_scraper.scrape(self.__ONE_ROW_INDEX)
            index, data = scrape_data.get_values()
            self.__dataframe.loc[index, self.__SCRAPE_COLUMNS] = data

        self.__dataframe = self.__dataframe.rename(columns=COLUMNS_MAPPING)
        drop_subset = self.__DROP_COLUMNS

        self.__dataframe = self.__dataframe.drop_duplicates(drop_subset)
        self.__dataframe = self.__dataframe.reset_index(drop=True)

        self.__dataframe = self.__similarity_filter.filter(self.__dataframe)
        result = rows_before - self.__dataframe.shape[0]
        total_loss = (result / rows_before) * 100

        LOG.info(f"Total articles loss: {total_loss:.2f}%")
        self.__dataframe.to_csv(FILE_PATH, sep=self.__SEP, index=False)

        return FileResponse(
            path=FILE_PATH,
            status_code=200,
            headers=HEADERS,
            media_type=self.__MEDIA_TYPE,
            filename=FILENAME,
        )

    def __multiple_web_scraping(self) -> None:
        cpu_count = len(sched_getaffinity(self.__PID))
        max_workers = min(self.__dataframe.shape[0], cpu_count)

        LOG.debug({"max_workers": max_workers})
        LOG.info("Performing Multiple Web Scraping")
        progress_bar = ProgressBar(self.__dataframe.shape[0])

        with (
            ProcessPoolExecutor(max_workers) as executor,
            logging_redirect_tqdm(LOG.logger),
        ):
            futures = [
                executor.submit(self.__articles_scraper.scrape, index)
                for index in range(self.__dataframe.shape[0])
            ]
            for future in as_completed(futures):
                index, data = future.result().get_values()
                self.__dataframe.loc[index, self.__SCRAPE_COLUMNS] = data

                progress_bar.step_progress()

            executor.shutdown(wait=True, cancel_futures=True)
            progress_bar.close()
