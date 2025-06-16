from itertools import combinations

from fastapi.responses import JSONResponse

from src.core.config.scopus import BOOLEAN_OPERATOR
from src.core.data.query_params import CombinationParams
from src.core.data.survey_detail import SurveyDetail
from src.core.domain.interfaces import SearchAPIABC


class SurveyKeywordsCombinations(KeywordsCombinationsABC):
    """Gathers, filters and compiles data from Scopus articles"""

    __MAX_SIZE = 5

    def __init__(
        self,
        search_api: SearchAPIABC,
        survey_detail: SurveyDetail,
    ) -> None:
        """Gathers, filters and compiles data from Scopus articles"""
        self.__search_api = search_api
        self.__survey_detail = survey_detail

    def survey_combinations(self, params: CombinationParams) -> JSONResponse:
        max_size = min(len(params.keywords) + 1, self.__MAX_SIZE)
        arrangements: list[str] = []

        for size in range(1, max_size):
            arrangement_batch = combinations(params.keywords, size)

            for arrangement in arrangement_batch:
                arrangements.append(BOOLEAN_OPERATOR.join(arrangement))

        for arrangement in arrangements:
            entry_items = self.__search_api.survey_results(arrangement)

        # disposition, ordination, line-up, arrangement, or combination
