# mypy: disable-error-code="index"
from asyncio import CancelledError
from unittest.mock import AsyncMock

from aiohttp_retry import RetryClient
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.common.error_messages import (
    ARTICLES_NOT_FOUND,
    CANCELLED_ERROR,
    QUOTA_EXCEEDED,
)
from src.utils.progress_bar import ProgressBar
from tests.conftest import assert_error_json
from tests.mocks.helpers import fqn, load_csv_from_response
from tests.mocks.integration import (
    SEARCH_CANCELLED_ERROR,
    SEARCH_MORE_PAGES_FULL_RESULTS,
    SEARCH_MORE_PAGES_PARTIAL_RESULTS,
    SEARCH_NO_QUOTA,
    SEARCH_NOT_FOUND,
    SEARCH_ONE_PAGE_FULL_RESULTS,
    SEARCH_ONE_PAGE_ONE_RESULT,
    SEARCH_ONE_QUOTA,
    SEARCH_TWO_PAGES_FULL_RESULTS,
    SEARCH_TWO_PAGES_PARTIAL_RESULTS,
    SURVEY_CANCELLED_ERROR,
    SURVEY_FOUR_KEYWORDS,
    SURVEY_NOT_FOUND,
    SURVEY_TWO_KEYWORDS,
)
from tests.mocks.raw import (
    COMBINATION_PARAMS,
    HTTP_200,
    HTTP_404,
    HTTP_429,
    HTTP_503,
    KEYWORDS,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_SEARCH,
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


@mark.asyncio
async def test_survey_cancelled_error(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SURVEY_CANCELLED_ERROR),
    )
    mocker.patch(STEP, side_effect=[None, None, CancelledError("any")])
    COMBINATION_PARAMS.update({"keywords": KEYWORDS})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_503, CANCELLED_ERROR)
    assert errors[0]["type"] == fqn(CancelledError)
    assert errors[0]["detail"] == "any" and mock.call_count == 8


@mark.asyncio
async def test_search_one_page_one_result(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SEARCH_ONE_PAGE_ONE_RESULT),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 2
    df = load_csv_from_response(res)
    assert df.shape[0] == 1


@mark.asyncio
async def test_search_one_page_full_results(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SEARCH_ONE_PAGE_FULL_RESULTS),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 26
    df = load_csv_from_response(res)
    assert df.shape[0] == 1


@mark.asyncio
async def test_search_two_pages_partial_results(
    mocker: Mocker, client: Client
):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SEARCH_TWO_PAGES_PARTIAL_RESULTS),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 32
    df = load_csv_from_response(res)
    assert df.shape[0] == 1


@mark.asyncio
async def test_search_two_pages_full_results(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SEARCH_TWO_PAGES_FULL_RESULTS),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 52
    df = load_csv_from_response(res)
    assert df.shape[0] == 1


@mark.asyncio
async def test_search_more_pages_partial_results(
    mocker: Mocker, client: Client
):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SEARCH_MORE_PAGES_PARTIAL_RESULTS),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 158
    df = load_csv_from_response(res)
    assert df.shape[0] == 1


@mark.asyncio
async def test_search_more_pages_full_results(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SEARCH_MORE_PAGES_FULL_RESULTS),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 182
    df = load_csv_from_response(res)
    assert df.shape[0] == 1


@mark.asyncio
async def test_search_not_found(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(return_value=SEARCH_NOT_FOUND),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    errors = assert_error_json(res, HTTP_404, ARTICLES_NOT_FOUND)
    assert errors is None and mock.call_count == 1


@mark.asyncio
@mark.parametrize(
    "response,count,total,per_page",
    [
        (SEARCH_EXACT_QUOTA_ONE_RESULT, 1, 1, 1),
        (SEARCH_EXACT_QUOTA_TWO_RESULTS, 2, 26, 25),
        (SEARCH_EXACT_QUOTA_MORE_RESULTS, 7, 151, 25),
    ],
    ids=["One result", "Two results", "More results"],
)
async def test_search_exact_quota_limit(
    mocker: Mocker,
    client: Client,
    response: list[MagicMock],
    count: int,
    total: int,
    per_page: int,
):
    state = mocker.patch(STATE, MockState(count, total))
    mock = mocker.patch(*get_patch(response))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    assert res.status_code == HTTP_200 and mock.call_count == count * 2
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == count and state.total_results == total
    assert state.items_per_page == per_page and state.pages_count == count


@mark.asyncio
@mark.parametrize(
    "response,count,total,per_page",
    [
        (SEARCH_NO_QUOTA_TWO_RESULTS, 1, 1, 25),
        (SEARCH_NO_QUOTA_MORE_RESULTS, 4, 76, 25),
    ],
    ids=["Two results", "More results"],
)
async def test_search_insufficient_quota(
    mocker: Mocker,
    client: Client,
    response: list[MagicMock],
    count: int,
    total: int,
    per_page: int,
):
    state = mocker.patch(STATE, MockState(count, total))
    mock = mocker.patch(*get_patch(response))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    assert res.status_code == HTTP_200 and mock.call_count == count * 2
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == count and state.total_results == total
    assert state.items_per_page == per_page and state.pages_count == count


@mark.asyncio
async def test_search_quota_exceeded(mocker: Mocker, client: Client):
    mock = mocker.patch(GET, new=AsyncMock(side_effect=SEARCH_NO_QUOTA))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    errors = assert_error_json(res, HTTP_429, QUOTA_EXCEEDED)
    assert errors is None and mock.call_count == 1


@mark.asyncio
async def test_search_cancelled_error(mocker: Mocker, client: Client):
    mocker.patch(STEP, side_effect=[None, None, CancelledError("any")])
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SEARCH_CANCELLED_ERROR),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    errors = assert_error_json(res, HTTP_503, CANCELLED_ERROR)
    assert errors[0]["type"] == fqn(CancelledError)
    assert errors[0]["detail"] == "any" and mock.call_count == 5
