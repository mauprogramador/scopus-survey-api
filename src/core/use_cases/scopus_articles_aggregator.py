from fastapi.responses import FileResponse
from pandas import DataFrame

from src.adapters.presenters.csv_response import CSVResponse
from src.core.common.types import SearchParams
from src.core.config.config import DIRECTORY, FILE, LOG
from src.core.data.enums import Column
from src.core.data.survey_detail import SurveyDetail
from src.core.domain.interfaces import (
    AbstractAPIABC,
    ArticlesAggregatorABC,
    SearchAPIABC,
    SimilarityFilterABC,
)


class ScopusArticlesAggregator(ArticlesAggregatorABC):
    """Gathers, filters and compiles data from Scopus articles"""

    __ROWS_INDEX = 0
    __NON_RATIO = 0
    __PERCENT = 100
    __SEP = ";"

    def __init__(
        self,
        search_api: SearchAPIABC,
        abstract_api: AbstractAPIABC,
        similarity_filter: SimilarityFilterABC,
        survey_detail: SurveyDetail,
    ) -> None:
        """Gathers, filters and compiles data from Scopus articles"""
        self.__search_api = search_api
        self.__abstract_api = abstract_api
        self.__similarity_filter = similarity_filter
        self.__survey_detail = survey_detail
        self.__dataframe: DataFrame = None

    def retrieve_articles(self, params: SearchParams) -> FileResponse:
        entry_items = self.__search_api.search_articles(params)
        self.__survey_detail.max_count = params.max_count

        self.__dataframe = self.__abstract_api.retrieve_abstracts(
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
        total_loss = (result / rows_before) * self.__PERCENT

        LOG.info(f"Total articles loss: \033[33;1m{total_loss:.2f}%")
        LOG.quota(*self.__survey_detail.log_data)

        file_path = DIRECTORY / f"{params.api_key}_{FILE}"
        self.__dataframe.to_csv(file_path, sep=self.__SEP, index=False)

        return CSVResponse.build(params.api_key, self.__survey_detail.headers)
