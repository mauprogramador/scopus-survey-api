from datetime import datetime

from fastapi.responses import FileResponse
from pandas import DataFrame

from src.adapters.presenters.csv_response import CSVResponse
from src.core.common.types import SearchParams
from src.core.config.config import DIRECTORY, FILE, LOG
from src.core.config.scopus import FOOTNOTE
from src.core.data.enums import Column
from src.core.domain.protocols import (
    AbstractAPI,
    SearchAPI,
    SimilarityFilter,
    SurveyDetail,
)


class ScopusArticlesAggregator:
    """Gathers, filters and compiles data from Scopus articles"""

    __DATEFMT = "%B %d, %Y"
    __ROWS_INDEX = 0
    __SINGLE_ROW = 1
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
        self._docs: DataFrame = None

    async def retrieve_articles(self, params: SearchParams) -> FileResponse:
        entry_items = await self.__search_api.search_articles(params)
        # self.__survey_detail.set_max_count(params.max_count)

        self._docs = await self.__abstract_api.retrieve_abstracts(
            params.api_key, entry_items
        )

        rows_in = self._docs.shape[self.__ROWS_INDEX]

        if rows_in != self.__SINGLE_ROW:
            self._docs = self._docs.drop_duplicates()
            self._docs = self._docs.reset_index(drop=True)

            self._docs = self._docs.drop_duplicates(Column.DROP)
            self._docs = self._docs.reset_index(drop=True)
            rows_out = self._docs.shape[self.__ROWS_INDEX]

        else:
            rows_out = self._docs.shape[self.__ROWS_INDEX]

        if rows_out != self.__SINGLE_ROW and params.ratio != self.__NON_RATIO:
            self._docs = self.__similarity_filter.filter(
                self._docs, params.ratio
            )

        result = rows_in - self._docs.shape[self.__ROWS_INDEX]
        loss = 0.0 if result == 0 else (result / rows_in) * self.__PERCENT
        self.__survey_detail.set_loss(loss)

        LOG.loss(rows_in, result, loss)
        LOG.quota(*self.__survey_detail.log_data)

        file_path = DIRECTORY / f"{params.api_key}_{FILE}"
        self._docs.to_csv(
            file_path,
            sep=self.__SEP,
            header=True,
            index=False,
            mode="w",
            encoding="utf-8",
        )

        with file_path.open(mode="a", encoding="utf-8") as file:
            date = datetime.now().strftime(self.__DATEFMT)
            file.write(FOOTNOTE.format(date=date))

        return CSVResponse.build(params.api_key, self.__survey_detail.headers)
