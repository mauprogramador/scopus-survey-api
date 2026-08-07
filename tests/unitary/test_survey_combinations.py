import random
from unittest.mock import AsyncMock

from pytest import mark

from src.adapters.gateway.scopus_volume_scouter import ScopusVolumeScouter
from src.adapters.serializers.query_params import CombinationParams
from src.adapters.serializers.scopus_data import ScopusHeaders
from src.adapters.types import Button, TotalBundle
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
    results, _ = await USE_CASE.process(params)

    assert len(results) == 3 and sum(item["total"] for item in results) > 0
    combinations_repr = ";".join(item["combination"] for item in results)

    for keyword in raw["keywords"]:
        assert keyword in combinations_repr


@mark.asyncio
async def test_survey_three_keywords():
    raw = {
        "api_key": API_KEY,
        "keywords": KEYWORDS[:3],
        "button": Button.COMBINATION.value,
    }
    params = CombinationParams(**raw)
    results, _ = await USE_CASE.process(params)

    assert len(results) == 7 and sum(item["total"] for item in results) > 0
    combinations_repr = ";".join(item["combination"] for item in results)

    for keyword in raw["keywords"]:
        assert keyword in combinations_repr


@mark.asyncio
async def test_survey_four_keywords():
    raw = {
        "api_key": API_KEY,
        "keywords": KEYWORDS,
        "button": Button.COMBINATION.value,
    }
    params = CombinationParams(**raw)
    results, _ = await USE_CASE.process(params)

    assert len(results) == 15 and sum(item["total"] for item in results) > 0
    combinations_repr = ";".join(item["combination"] for item in results)

    for keyword in raw["keywords"]:
        assert keyword in combinations_repr
