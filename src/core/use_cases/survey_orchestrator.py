from fastapi.responses import FileResponse
from pandas import DataFrame

from src.adapters.presenters.csv_response import csv_response
from src.core.common.types import (
    AbstractAPI,
    SearchAPI,
    SimilarityFilter,
    SurveyDetails,
    SurveyParams,
)
from src.core.data.csv_builder import write_csv_file
from src.utils import logger


class SurveyOrchestrator:
    """Gathers, filters and compiles data from Scopus articles"""

    _COLUMNS = ["title", "authors"]
    _SINGLE_ROW = 1
    _NON_RATIO = 0

    def __init__(
        self,
        search_api: SearchAPI,
        abstract_api: AbstractAPI,
        similarity_filter: SimilarityFilter,
        survey_details: SurveyDetails,
    ) -> None:
        """Gathers, filters and compiles data from Scopus articles"""
        self._search_api = search_api
        self._abstract_api = abstract_api
        self._similarity_filter = similarity_filter
        self._details = survey_details
        self._docs: DataFrame = None

    async def retrieve_articles(self, params: SurveyParams) -> FileResponse:
        self._details.set_combination(params.combination)

        try:
            await self._search_api.search_articles(params)
            self._docs = await self._abstract_api.retrieve_abstracts(
                params.api_key
            )
        finally:
            await self._search_api.http_client.close()

        initial_count = self._docs.shape[0]
        rows_out = self._SINGLE_ROW

        if initial_count != self._SINGLE_ROW:
            self._docs = self._docs.drop_duplicates()
            self._docs = self._docs.reset_index(drop=True)

            self._docs = self._docs.drop_duplicates(self._COLUMNS)
            self._docs = self._docs.reset_index(drop=True)
            rows_out = self._docs.shape[0]

        if rows_out != self._SINGLE_ROW and params.ratio != self._NON_RATIO:
            self._docs = self._similarity_filter.filter(
                self._docs, params.ratio
            )

        final = initial_count - self._docs.shape[0]
        loss = 0.0 if final == 0 else (final / initial_count) * 100.0  # %
        self._details.set_loss(final, loss)

        logger.loss(initial_count, final, loss)
        logger.quota(*self._details.search_quota)
        logger.quota(*self._details.abstract_quota)

        filename = write_csv_file(self._docs, params, self._details.metadata)

        return csv_response(filename, params.api_key, self._details.headers)
