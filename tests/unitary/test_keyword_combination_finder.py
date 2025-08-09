from json import loads
from unittest.mock import AsyncMock, MagicMock, Mock

from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.adapters.gateway.scopus_search_api import ScopusSearchAPI
from src.adapters.helpers.url_builder import URLBuilder
from src.core.common.types import Json
from src.core.data.enums import Button
from src.core.data.query_params import CombinationParams
from src.core.data.survey_detail import SurveyDetail
from src.core.use_cases.keyword_combination_finder import (
    KeywordCombinationFinder,
)
from tests.mocks.helpers import (
    fqn,
    mock_combination_url,
    mock_survey_totals_found,
)
from tests.mocks.raw import API_KEY, HTTP_200, KEYWORDS, LOG_DATA

COMBINATION_FINDER = KeywordCombinationFinder(
    MagicMock(
        spec=URLBuilder,
        combination_url=Mock(side_effect=mock_combination_url),
    ),
    AsyncMock(
        spec=ScopusSearchAPI,
        survey_totals_found=AsyncMock(side_effect=mock_survey_totals_found),
    ),
    MagicMock(spec=SurveyDetail, log_data=LOG_DATA),
)
RANDINT = fqn(mock_survey_totals_found, "randint")


@mark.asyncio
async def test_survey_two_keywords():
    raw = {
        "api_key": API_KEY,
        "keywords": KEYWORDS[:2],
        "button": Button.COMBINATION.value,
    }
    params = CombinationParams(**raw)

    result = await COMBINATION_FINDER.survey_combinations(params)
    data: Json = loads(result.body.decode())  # type: ignore

    assert result.status_code == HTTP_200
    assert len(data["combinations"]) == 3
    assert sum(item["total"] for item in data["combinations"]) > 0


@mark.asyncio
async def test_survey_three_keywords():
    raw = {
        "api_key": API_KEY,
        "keywords": KEYWORDS[:3],
        "button": Button.COMBINATION.value,
    }
    params = CombinationParams(**raw)

    result = await COMBINATION_FINDER.survey_combinations(params)
    data: Json = loads(result.body.decode())  # type: ignore

    assert result.status_code == HTTP_200
    assert len(data["combinations"]) == 7
    assert sum(item["total"] for item in data["combinations"]) > 0


@mark.asyncio
async def test_survey_four_keywords():
    raw = {
        "api_key": API_KEY,
        "keywords": KEYWORDS,
        "button": Button.COMBINATION.value,
    }
    params = CombinationParams(**raw)

    result = await COMBINATION_FINDER.survey_combinations(params)
    data: Json = loads(result.body.decode())  # type: ignore

    assert result.status_code == HTTP_200
    assert len(data["combinations"]) == 15
    assert sum(item["total"] for item in data["combinations"]) > 0


@mark.asyncio
async def test_survey_not_found(mocker: Mocker):
    mocker.patch(RANDINT, return_value=0)
    raw = {
        "api_key": API_KEY,
        "keywords": KEYWORDS[:2],
        "button": Button.COMBINATION.value,
    }
    params = CombinationParams(**raw)

    result = await COMBINATION_FINDER.survey_combinations(params)
    data: Json = loads(result.body.decode())  # type: ignore

    assert result.status_code == HTTP_200
    assert len(data["combinations"]) == 3
    assert sum(item["total"] for item in data["combinations"]) == 0
