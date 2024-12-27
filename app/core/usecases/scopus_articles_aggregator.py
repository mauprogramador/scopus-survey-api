from http import HTTPStatus
from os.path import join

from fastapi.responses import FileResponse
from pandas import DataFrame

from app.core.config.config import DIRECTORY, FILE, LOG
from app.core.config.scopus import AUTHORS_COLUMN, TITLE_COLUMN
from app.core.data.serializers import CSVFileHeaders
from app.core.data.validators import SearchParams
from app.core.domain.metaclasses import (
    AbstractAPI,
    ArticlesAggregator,
    SearchAPI,
    SimilarityFilter,
)


class ScopusArticlesAggregator(ArticlesAggregator):
    """Gathers, filters and compiles data from Scopus articles"""

    __DROP_COLUMNS = [TITLE_COLUMN, AUTHORS_COLUMN]
    __MEDIA_TYPE = "text/csv"
    __ROWS_INDEX = 0
    __PERCENT = 100
    __SEP = ";"

    def __init__(
        self,
        search_api: SearchAPI,
        abstract_api: AbstractAPI,
        similarity_filter: SimilarityFilter,
    ) -> None:
        """Gathers, filters and compiles data from Scopus articles"""
        self.__search_api = search_api
        self.__abstract_api = abstract_api
        self.__similarity_filter = similarity_filter
        self.__dataframe: DataFrame = None

    def get_articles(self, params: SearchParams) -> FileResponse:
        entry_items = self.__search_api.search_articles(params)
        self.__dataframe = self.__abstract_api.retrieve_abstracts(
            params.api_key, entry_items
        )

        rows_before = self.__dataframe.shape[self.__ROWS_INDEX]
        self.__dataframe = self.__dataframe.drop_duplicates()
        self.__dataframe = self.__dataframe.reset_index(drop=True)

        drop_subset = self.__DROP_COLUMNS
        self.__dataframe = self.__dataframe.drop_duplicates(drop_subset)
        self.__dataframe = self.__dataframe.reset_index(drop=True)

        self.__dataframe = self.__similarity_filter.filter(self.__dataframe)
        result = rows_before - self.__dataframe.shape[self.__ROWS_INDEX]
        total_loss = (result / rows_before) * self.__PERCENT

        LOG.info(f"Total articles loss: {total_loss:.2f}%")

        filename = f"{params.api_key}_{FILE}"
        file_path = join(DIRECTORY, filename)

        self.__dataframe.to_csv(file_path, sep=self.__SEP, index=False)
        headers = CSVFileHeaders.build(filename, params.api_key)

        return FileResponse(
            path=file_path,
            status_code=HTTPStatus.OK,
            headers=headers,
            media_type=self.__MEDIA_TYPE,
            filename=filename,
        )
