# mypy: disable-error-code="index"
from asyncio import CancelledError
from unittest.mock import AsyncMock

from aiohttp_retry import RetryClient
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.common.error_messages import ARTICLES_NOT_FOUND, CANCELLED_ERROR
from src.utils.progress_bar import ProgressBar
from tests.conftest import assert_error_json
from tests.mocks.helpers import fqn, load_csv_file_response_dataframe
from tests.mocks.integration import (
    SEARCH_CANCELLED_ERROR,
    SEARCH_MORE_PAGES_FULL_RESULTS,
    SEARCH_MORE_PAGES_PARTIAL_RESULTS,
    SEARCH_NOT_FOUND,
    SEARCH_ONE_PAGE_FULL_RESULTS,
    SEARCH_ONE_PAGE_ONE_RESULT,
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
    HTTP_503,
    KEYWORDS,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_SEARCH,
)

# SET_COUNT_LIMIT = fqn(ScopusSearch.set_count_limit)
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
    df = load_csv_file_response_dataframe(res)
    assert df.shape[0] == 1


@mark.asyncio
async def test_search_one_page_full_results(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SEARCH_ONE_PAGE_FULL_RESULTS),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 26
    df = load_csv_file_response_dataframe(res)
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
    df = load_csv_file_response_dataframe(res)
    assert df.shape[0] == 1


@mark.asyncio
async def test_search_two_pages_full_results(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SEARCH_TWO_PAGES_FULL_RESULTS),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 52
    df = load_csv_file_response_dataframe(res)
    assert df.shape[0] == 1


@mark.asyncio
async def test_search_more_pages_partial_results(
    mocker: Mocker, client: Client
):
    # mocker.patch(SET_COUNT_LIMIT)
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SEARCH_MORE_PAGES_PARTIAL_RESULTS),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 158
    df = load_csv_file_response_dataframe(res)
    assert df.shape[0] == 1


@mark.asyncio
async def test_search_more_pages_full_results(mocker: Mocker, client: Client):
    # mocker.patch(SET_COUNT_LIMIT)
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SEARCH_MORE_PAGES_FULL_RESULTS),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 182
    df = load_csv_file_response_dataframe(res)
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


# @mark.asyncio
# async def test_search_count_limit_default(mocker: Mocker, client: CLient):
#     ?????


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
