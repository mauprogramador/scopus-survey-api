from http import HTTPStatus
from itertools import chain, combinations

from fastapi.responses import JSONResponse

from src.core.common.types import CombinationBundle
from src.core.config.config import LOG
from src.core.data.query_params import CombinationParams
from src.core.data.survey_detail import SurveyDetail
from src.core.domain.protocols import SearchAPI, URLBuilder


class KeywordCombinationFinder:
    """Gathers, filters and compiles data from Scopus articles"""

    __MEDIA_TYPE = "application/json"
    __MAX_SIZE = 5
    __START = 1

    def __init__(
        self,
        url_builder: URLBuilder,
        search_api: SearchAPI,
        survey_detail: SurveyDetail,
    ) -> None:
        """Gathers, filters and compiles data from Scopus articles"""
        self.__url_builder = url_builder
        self.__search_api = search_api
        self.__survey_detail = survey_detail

    async def survey_combinations(
        self, params: CombinationParams
    ) -> JSONResponse:
        self.__url_builder.set_combination_query(params)

        max_size = min(len(params.keywords) + self.__START, self.__MAX_SIZE)
        bundles_map: dict[int, CombinationBundle] = {}

        arrangements = (
            combinations(params.keywords, size)
            for size in range(self.__START, max_size)
        )

        pairs = chain.from_iterable(arrangements)
        for index, arrangement in enumerate(pairs, self.__START):
            bundle = self.__url_builder.combination_url(arrangement)

            bundle.index = index
            bundles_map.setdefault(index, bundle)

        survey_list = await self.__search_api.survey_combinations(bundles_map)
        LOG.combinations(len(params.keywords), survey_list)
        LOG.quota(*self.__survey_detail.log_data)

        headers = self.__survey_detail.headers
        headers.update({"X-API-Key": params.api_key})
        headers.update({"Content-Type": "application/json; charset=utf-8"})

        return JSONResponse(
            content={"combinations": survey_list},
            status_code=HTTPStatus.OK,
            headers=headers,
            media_type=self.__MEDIA_TYPE,
        )
