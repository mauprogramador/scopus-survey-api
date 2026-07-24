# mypy: disable-error-code="index"
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from tests.mocks.helpers import get_patch
from tests.mocks.integration import (
    SURVEY_FOUR_KEYWORDS,
    SURVEY_NOT_FOUND,
    SURVEY_TWO_KEYWORDS,
)
from tests.mocks.raw import (
    COMBINATION_PARAMS,
    HTTP_200,
    KEYWORDS,
    URL_COMBINATION,
)


@mark.asyncio
async def test_scouter_combinations(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(SURVEY_TWO_KEYWORDS))
    mocker.patch.dict(COMBINATION_PARAMS, {"keywords": KEYWORDS[:2]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3
    combs = res.json()["result"]["combinations"]
    assert len(combs) == 3 and sum(item["total"] for item in combs) == 3


@mark.asyncio
async def test_scouter_more_combinations(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(SURVEY_FOUR_KEYWORDS))
    mocker.patch.dict(COMBINATION_PARAMS, {"keywords": KEYWORDS})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 15
    combs = res.json()["result"]["combinations"]
    assert len(combs) == 15 and sum(item["total"] for item in combs) == 15


@mark.asyncio
async def test_scouter_not_found(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(SURVEY_NOT_FOUND))
    mocker.patch.dict(COMBINATION_PARAMS, {"keywords": KEYWORDS[:2]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3
    combs = res.json()["result"]["combinations"]
    assert len(combs) == 3 and sum(item["total"] for item in combs) == 0
