from typing import Any
from unittest.mock import AsyncMock

from pytest import mark

from src.adapters.gateway.scopus_volume_scouter import ScopusVolumeScouter
from src.adapters.serializers.query_params import CombinationParams
from src.infra.http.http_client import HTTPClient
from tests.mocks.raw import ALIAS_COMBINATION_PARAMS
from tests.mocks.unitary import SURVEY_MAP, SURVEY_NOT_FOUND, SURVEY_RESULTS


PARAMS = CombinationParams(**ALIAS_COMBINATION_PARAMS)


def _fixt(value: Any | Exception) -> tuple[ScopusVolumeScouter, AsyncMock]:
    if isinstance(value, (list, BaseException)):
        api_call_mock = AsyncMock(HTTPClient.api_call, side_effect=value)
    else:
        api_call_mock = AsyncMock(HTTPClient.api_call, return_value=value)

    api = ScopusVolumeScouter(AsyncMock(HTTPClient, api_call=api_call_mock))
    return api, api_call_mock


@mark.asyncio
async def test_scouter_combinations():
    gateway, api_call = _fixt(SURVEY_RESULTS[:3])
    results, headers = await gateway.fetch(PARAMS, ["any"] * 3)

    assert len(results) == 3 and api_call.call_count == 3
    assert sum(item["total"] for item in results) != 0
    assert headers.status == "OK"

    for item in results:
        search_results = SURVEY_MAP[item["index"]].data["search-results"]
        assert search_results["opensearch:totalResults"] == str(item["total"])


@mark.asyncio
async def test_scouter_more_combinations():
    gateway, api_call = _fixt(SURVEY_RESULTS)
    results, headers = await gateway.fetch(PARAMS, ["any"] * 15)

    assert len(results) == 15 and api_call.call_count == 15
    assert sum(item["total"] for item in results) != 0
    assert headers.status == "OK"

    for item in results:
        search_results = SURVEY_MAP[item["index"]].data["search-results"]
        assert search_results["opensearch:totalResults"] == str(item["total"])


@mark.asyncio
async def test_scouter_not_found():
    gateway, api_call = _fixt(SURVEY_NOT_FOUND)
    results, headers = await gateway.fetch(PARAMS, ["any"] * 3)

    assert len(results) == 3 and api_call.call_count == 3
    assert sum(item["total"] for item in results) == 0
    assert headers.status == "OK"


@mark.asyncio
async def test_scouter_sort_order():
    gateway, api_call = _fixt(SURVEY_RESULTS[:3])
    results, headers = await gateway.fetch(PARAMS, ["any"] * 3)

    assert len(results) == 3 and api_call.call_count == 3
    assert sum(item["total"] for item in results) != 0
    assert headers.status == "OK"

    for index in range(3):
        assert results[index]["index"] == index + 1  # start=1
