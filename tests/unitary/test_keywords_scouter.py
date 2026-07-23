import random
from unittest.mock import AsyncMock

from pytest import mark

from src.adapters.gateway.scopus_search_api import ScopusVolumeScouter
from src.core.common.types import TotalBundle
from src.core.data.enums import Button
from src.core.data.query_params import CombinationParams
from src.core.data.serializers import ScopusHeaders
from src.core.use_cases.survey_combinations import SurveyCombinations
from tests.mocks.raw import API_KEY, KEYWORDS, RAW_HEADERS_OK


async def _mock_fetch(
    params: CombinationParams,  # pylint: disable=w0613
    combinations: list[str],
) -> tuple[list[TotalBundle], ScopusHeaders]:
    results: list[TotalBundle] = []
    for index, combination in enumerate(combinations, start=1):
        data: TotalBundle = {
            "index": index,
            "combination": combination,
            "total": random.randint(0, 256),
        }
        results.append(data)
    return results, ScopusHeaders(**RAW_HEADERS_OK)


USE_CASE = SurveyCombinations(
    AsyncMock(
        ScopusVolumeScouter,
        fetch=AsyncMock(ScopusVolumeScouter.fetch, side_effect=_mock_fetch),
    ),
)


@mark.asyncio
async def test_survey_two_keywords():
    raw = {
        "api_key": API_KEY,
        "keywords": KEYWORDS[:2],
        "button": Button.COMBINATION.value,
    }
    params = CombinationParams(**raw)

    res = await COMBINATION_FINDER.survey_combinations(params)
    result: Json = json.loads(res.body.decode())["result"]  # type: ignore

    assert res.status_code == HTTP_200
    assert len(result["combinations"]) == 3
    assert sum(item["total"] for item in result["combinations"]) > 0


@mark.asyncio
async def test_survey_three_keywords():
    raw = {
        "api_key": API_KEY,
        "keywords": KEYWORDS[:3],
        "button": Button.COMBINATION.value,
    }
    params = CombinationParams(**raw)

    res = await COMBINATION_FINDER.survey_combinations(params)
    result: Json = json.loads(res.body.decode())["result"]  # type: ignore

    assert res.status_code == HTTP_200
    assert len(result["combinations"]) == 7
    assert sum(item["total"] for item in result["combinations"]) > 0


@mark.asyncio
async def test_survey_four_keywords():
    raw = {
        "api_key": API_KEY,
        "keywords": KEYWORDS,
        "button": Button.COMBINATION.value,
    }
    params = CombinationParams(**raw)

    res = await COMBINATION_FINDER.survey_combinations(params)
    result: Json = json.loads(res.body.decode())["result"]  # type: ignore

    assert res.status_code == HTTP_200
    assert len(result["combinations"]) == 15
    assert sum(item["total"] for item in result["combinations"]) > 0


@mark.asyncio
async def test_survey_not_found(mocker: Mocker):
    mocker.patch(**RANDINT(0))
    raw = {
        "api_key": API_KEY,
        "keywords": KEYWORDS[:2],
        "button": Button.COMBINATION.value,
    }
    params = CombinationParams(**raw)

    res = await COMBINATION_FINDER.survey_combinations(params)
    result: Json = json.loads(res.body.decode())["result"]  # type: ignore

    assert res.status_code == HTTP_200
    assert len(result["combinations"]) == 3
    assert sum(item["total"] for item in result["combinations"]) == 0
