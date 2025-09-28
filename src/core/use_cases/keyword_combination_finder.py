from itertools import chain, combinations

from fastapi.responses import JSONResponse

from src.adapters.presenters.json_response import SuccessJSON
from src.core.common.types import CombinationBundle
from src.core.config.config import LOG
from src.core.data.query_params import CombinationParams
from src.core.data.survey_detail import SurveyDetails
from src.core.domain.protocols import SearchAPI, URLBuilder


class KeywordCombinationFinder:
    """Gathers, filters and compiles data from Scopus articles"""

    _MAX_SIZE = 5
    _START = 1

    def __init__(
        self,
        url_builder: URLBuilder,
        search_api: SearchAPI,
        survey_detail: SurveyDetails,
    ) -> None:
        """Gathers, filters and compiles data from Scopus articles"""
        self._url_builder = url_builder
        self._search_api = search_api
        self._survey_detail = survey_detail

    async def survey_combinations(
        self, params: CombinationParams
    ) -> JSONResponse:
        self._url_builder.set_combination_query(params)

        max_size = min(len(params.keywords) + self._START, self._MAX_SIZE)
        bundles_map: dict[int, CombinationBundle] = {}

        arrangements = (
            combinations(params.keywords, size)
            for size in range(self._START, max_size)
        )

        pairs = chain.from_iterable(arrangements)
        for index, arrangement in enumerate(pairs, self._START):
            bundle = self._url_builder.combination_url(arrangement)

            bundle.index = index
            bundles_map.setdefault(index, bundle)

        survey_list = await self._search_api.survey_totals_found(bundles_map)
        totals: list[int] = [data["total"] for data in survey_list]
        nkeywords, average = len(params.keywords), 0.0

        if sum(totals) > 0:
            square_totals_sum = sum(total * total for total in totals)
            average = square_totals_sum / (nkeywords * sum(totals))

        average = int(average)
        self._survey_detail.set_average_found(average)

        LOG.combinations(nkeywords, totals, average)
        LOG.quota(*self._survey_detail.log_data)

        headers = self._survey_detail.headers
        headers.update({"X-API-Key": params.api_key})
        headers.update({"Content-Type": "application/json; charset=utf-8"})

        return SuccessJSON(
            data={"combinations": survey_list},
            message="Combination totals survey successfully",
            headers=headers,
        )
