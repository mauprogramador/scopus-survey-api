from unittest.mock import AsyncMock

from aiohttp_retry import RetryClient
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.utils.progress_bar import ProgressBar
from tests.mocks.helpers import fqn
from tests.mocks.integration import (
    SURVEY_FOUR_KEYWORDS,
    SURVEY_NOT_FOUND,
    SURVEY_THREE_KEYWORDS,
    SURVEY_TWO_KEYWORDS,
)
from tests.mocks.raw import (
    COMBINATION_PARAMS,
    HTTP_200,
    KEYWORDS,
    URL_COMBINATION,
)

STEP = fqn(ProgressBar.step)
GET = fqn(RetryClient.get)


@mark.asyncio
async def test_survey_two_keywords(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SURVEY_TWO_KEYWORDS),
    )
    COMBINATION_PARAMS.update({"keywords": KEYWORDS[:2]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3
    combs = res.json()["data"]["combinations"]
    assert len(combs) == 3 and sum(item["total"] for item in combs) == 3


@mark.asyncio
async def test_survey_three_keywords(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SURVEY_THREE_KEYWORDS),
    )
    COMBINATION_PARAMS.update({"keywords": KEYWORDS[:3]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 7
    combs = res.json()["data"]["combinations"]
    assert len(combs) == 7 and sum(item["total"] for item in combs) == 7


@mark.asyncio
async def test_survey_four_keywords(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SURVEY_FOUR_KEYWORDS),
    )
    COMBINATION_PARAMS.update({"keywords": KEYWORDS})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 15
    combs = res.json()["data"]["combinations"]
    assert len(combs) == 15 and sum(item["total"] for item in combs) == 15


@mark.asyncio
async def test_survey_not_found(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SURVEY_NOT_FOUND),
    )
    COMBINATION_PARAMS.update({"keywords": KEYWORDS[:2]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3
    combs = res.json()["data"]["combinations"]
    assert len(combs) == 3 and sum(item["total"] for item in combs) == 0
