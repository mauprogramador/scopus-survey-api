from csv import writer
from datetime import datetime

from fastapi.responses import FileResponse
from pandas import DataFrame

from src.adapters.presenters.csv_response import CSVResponse
from src.core.common.types import SearchParams
from src.core.config.config import DIRECTORY, FILE, LOG
from src.core.data.enums import Column
from src.core.domain.protocols import (
    AbstractAPI,
    SearchAPI,
    SimilarityFilter,
    SurveyDetail,
)


class ScopusArticlesAggregator:
    """Gathers, filters and compiles data from Scopus articles"""

    __FOOTNOTE = (
        "\n# The data was retrieved from Scopus API on {date} via "
        "http://api.elsevier.com and http://www.scopus.com.\n"
    )
    __DATEFMT = "%B %d, %Y"
    __ROWS_INDEX = 0
    __PERCENT = 100
    __NON_RATIO = 0
    __SEP = ";"

    def __init__(
        self,
        search_api: SearchAPI,
        abstract_api: AbstractAPI,
        similarity_filter: SimilarityFilter,
        survey_detail: SurveyDetail,
    ) -> None:
        """Gathers, filters and compiles data from Scopus articles"""
        self.__search_api = search_api
        self.__abstract_api = abstract_api
        self.__similarity_filter = similarity_filter
        self.__survey_detail = survey_detail
        self.__dataframe: DataFrame = None

    async def retrieve_articles(self, params: SearchParams) -> FileResponse:
        entry_items = await self.__search_api.search_articles(params)
        self.__survey_detail.set_max_count(params.max_count)

        self.__dataframe = await self.__abstract_api.retrieve_abstracts(
            params.api_key, entry_items
        )

        rows_before = self.__dataframe.shape[self.__ROWS_INDEX]
        self.__dataframe = self.__dataframe.drop_duplicates()
        self.__dataframe = self.__dataframe.reset_index(drop=True)

        self.__dataframe = self.__dataframe.drop_duplicates(Column.DROP)
        self.__dataframe = self.__dataframe.reset_index(drop=True)

        if params.ratio != self.__NON_RATIO:
            self.__dataframe = self.__similarity_filter.filter(
                self.__dataframe, params.ratio
            )

        result = rows_before - self.__dataframe.shape[self.__ROWS_INDEX]
        loss = 0.0 if result == 0 else (result / rows_before) * self.__PERCENT
        self.__survey_detail.set_loss(loss)

        LOG.loss(rows_before, result, loss)
        LOG.quota(*self.__survey_detail.log_data)

        file_path = DIRECTORY / f"{params.api_key}_{FILE}"
        self.__dataframe.to_csv(
            file_path,
            sep=self.__SEP,
            header=True,
            index=False,
            mode="w",
            encoding="utf-8",
        )

        with open(file_path, mode="a", encoding="utf-8", newline="") as file:
            current_dt = datetime.now()
            date = current_dt.strftime(self.__DATEFMT)

            csv = writer(file, delimiter=self.__SEP)
            csv.writerow(self.__FOOTNOTE.format(date=date))

        return CSVResponse.build(params.api_key, self.__survey_detail.headers)
