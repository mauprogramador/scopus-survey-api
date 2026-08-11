from pandas import DataFrame

from src.core.domain.types import (
    DatasetGatherer,
    SimilarityFilter,
    SurveyDetails,
    SurveyParams,
)
from src.infra.utils import logger


class SurveyAggregator:
    """Gathers, filters and compiles data from Scopus articles"""

    _COLUMNS = ["title", "authors"]
    _SINGLE_ROW = 1
    _NON_RATIO = 0

    def __init__(
        self,
        api_gateway: DatasetGatherer,
        similarity_filter: SimilarityFilter,
    ) -> None:
        """Gathers, filters and compiles data from Scopus articles"""
        self._api_gateway = api_gateway
        self._similarity_filter = similarity_filter

    async def process(
        self, params: SurveyParams
    ) -> tuple[DataFrame, SurveyDetails]:
        raw_dataset, scopus_details = await self._api_gateway.fetch(params)

        dataset = DataFrame(raw_dataset)
        initial_row_count = dataset.shape[0]

        if dataset.shape[0] != self._SINGLE_ROW:
            dup_mask_full = dataset.duplicated(keep="first")

            dropped_full = dataset[dup_mask_full]
            logger.debug(dropped_full=dropped_full)

            dataset = dataset[~dup_mask_full]

        if dataset.shape[0] != self._SINGLE_ROW:
            dup_mask_sub = dataset.duplicated(
                subset=self._COLUMNS, keep="first"
            )

            dropped_sub = dataset[dup_mask_sub]
            logger.debug(dropped_sub=dropped_sub)

            dataset = dataset[~dup_mask_sub]

        dataset = dataset.reset_index(drop=True)

        if (
            dataset.shape[0] != self._SINGLE_ROW
            and params.ratio != self._NON_RATIO
        ):
            dataset = self._similarity_filter.filter(dataset, params.ratio)

        logger.loss(initial_row_count, dataset.shape[0])

        details = SurveyDetails(*scopus_details, dataset.shape[0])

        return dataset, details
