from fastapi.responses import FileResponse
from pandas import DataFrame

from app.core.config.config import FILE_PATH, FILENAME, HEADERS, LOG
from app.core.config.scopus import AUTHORS_COLUMN, TITLE_COLUMN
from app.core.data.dtos import SearchParams
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

        rows_before = self.__dataframe.shape[0]
        self.__dataframe = self.__dataframe.drop_duplicates()
        self.__dataframe = self.__dataframe.reset_index(drop=True)

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
