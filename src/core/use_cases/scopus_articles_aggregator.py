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

    _DATEFMT = "%B %d, %Y"
    _ROWS_INDEX = 0
    _SINGLE_ROW = 1
    _PERCENT = 100
    _NON_RATIO = 0
    _SEP = ";"

    def __init__(
        self,
        search_api: SearchAPI,
        abstract_api: AbstractAPI,
        similarity_filter: SimilarityFilter,
        survey_detail: SurveyDetail,
    ) -> None:
        """Gathers, filters and compiles data from Scopus articles"""
        self._search_api = search_api
        self._abstract_api = abstract_api
        self._similarity_filter = similarity_filter
        self._survey_detail = survey_detail
        self._docs: DataFrame = None

    async def retrieve_articles(self, params: SearchParams) -> FileResponse:
        entry_items = await self._search_api.search_articles(params)
        # self._survey_detail.set_max_count(params.max_count)

        self._docs = await self._abstract_api.retrieve_abstracts(
            params.api_key, entry_items
        )

        rows_in = self._docs.shape[self._ROWS_INDEX]

        if rows_in != self._SINGLE_ROW:
            self._docs = self._docs.drop_duplicates()
            self._docs = self._docs.reset_index(drop=True)

            self._docs = self._docs.drop_duplicates(Column.DROP)
            self._docs = self._docs.reset_index(drop=True)
            rows_out = self._docs.shape[self._ROWS_INDEX]

        else:
            rows_out = self._docs.shape[self._ROWS_INDEX]

        if rows_out != self._SINGLE_ROW and params.ratio != self._NON_RATIO:
            self._docs = self._similarity_filter.filter(
                self._docs, params.ratio
            )

        result = rows_in - self._docs.shape[self._ROWS_INDEX]
        loss = 0.0 if result == 0 else (result / rows_in) * self._PERCENT
        self._survey_detail.set_loss(loss)

        LOG.loss(rows_in, result, loss)
        LOG.quota(*self._survey_detail.log_data)

        file_path = DIRECTORY / f"{params.api_key}_{FILE}"
        self._docs.to_csv(
            file_path,
            sep=self._SEP,
            header=True,
            index=False,
            mode="w",
            encoding="utf-8",
        )

        with file_path.open(mode="a", encoding="utf-8") as file:
            date = datetime.now().strftime(self._DATEFMT)
            file.write(FOOTNOTE.format(date=date))

        return CSVResponse.build(params.api_key, self._survey_detail.headers)
