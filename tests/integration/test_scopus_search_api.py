# mypy: disable-error-code="index"
from asyncio import CancelledError
from unittest.mock import MagicMock

from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.adapters.gateway.scopus_search_api import ScopusSearchAPI
from src.adapters.helpers.scopus_response import ScopusResponse
from src.core.common.error_messages import ARTICLES_NOT_FOUND, CANCELLED_ERROR
from src.core.data.enums import ScopusCode
from src.core.data.quota_results_handler import QuotaResultsHandler
from src.core.domain.factory import make_aggregator
from src.utils.progress_bar import ProgressBar
from tests.conftest import assert_error_json
from tests.mocks.errors import MORE_CANCELLED
from tests.mocks.helpers import (
    MockState,
    Patch,
    fqn,
    get_patch,
    load_csv_from_response,
)
from tests.mocks.integration import (
    SEARCH_EXACT_QUOTA_MORE_RESULTS,
    SEARCH_EXACT_QUOTA_ONE_RESULT,
    SEARCH_EXACT_QUOTA_TWO_RESULTS,
    SEARCH_MORE_PAGES_FULL_RESULTS,
    SEARCH_MORE_PAGES_PARTIAL_RESULTS,
    SEARCH_NO_QUOTA_MORE_RESULTS,
    SEARCH_NO_QUOTA_TWO_RESULTS,
    SEARCH_NOT_FOUND,
    SEARCH_ONE_PAGE_FULL_RESULTS,
    SEARCH_ONE_PAGE_ONE_RESULT,
    SEARCH_QUOTA_EXCEEDED,
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
    HTTP_502,
    HTTP_503,
    KEYWORDS,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_SEARCH,
)


STATE = fqn(make_aggregator, QuotaResultsHandler)
STEP = Patch(ScopusSearchAPI, ProgressBar(0).step)


@mark.asyncio
async def test_survey_two_keywords(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(SURVEY_TWO_KEYWORDS))
    COMBINATION_PARAMS.update({"keywords": KEYWORDS[:2]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3
    combs = res.json()["data"]["combinations"]
    assert len(combs) == 3 and sum(item["total"] for item in combs) == 3


@mark.asyncio
async def test_survey_four_keywords(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(SURVEY_FOUR_KEYWORDS))
    COMBINATION_PARAMS.update({"keywords": KEYWORDS})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 15
    combs = res.json()["data"]["combinations"]
    assert len(combs) == 15 and sum(item["total"] for item in combs) == 15


@mark.asyncio
async def test_survey_not_found(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(SURVEY_NOT_FOUND))
    COMBINATION_PARAMS.update({"keywords": KEYWORDS[:2]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3
    combs = res.json()["data"]["combinations"]
    assert len(combs) == 3 and sum(item["total"] for item in combs) == 0


@mark.asyncio
async def test_survey_cancelled_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(SURVEY_CANCELLED_ERROR))
    mocker.patch(**STEP(MORE_CANCELLED))
    COMBINATION_PARAMS.update({"keywords": KEYWORDS})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_503, CANCELLED_ERROR)
    assert errors[0]["type"] == fqn(CancelledError)
    assert errors[0]["detail"] == "any" and mock.call_count == 8


@mark.asyncio
async def test_search_one_page_one_result(mocker: Mocker, client: Client):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(SEARCH_ONE_PAGE_ONE_RESULT))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    assert res.status_code == HTTP_200 and mock.call_count == 2
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == 1 and state.total_results == 1
    assert state.items_per_page == 1 and state.pages_count == 1


@mark.asyncio
async def test_search_one_page_full_results(mocker: Mocker, client: Client):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(SEARCH_ONE_PAGE_FULL_RESULTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    assert res.status_code == HTTP_200 and mock.call_count == 2
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == 1 and state.total_results == 25
    assert state.items_per_page == 25 and state.pages_count == 1


@mark.asyncio
async def test_search_two_pages_partial_results(
    mocker: Mocker, client: Client
):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(SEARCH_TWO_PAGES_PARTIAL_RESULTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    assert res.status_code == HTTP_200 and mock.call_count == 4
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == 2 and state.total_results == 30
    assert state.items_per_page == 25 and state.pages_count == 2


@mark.asyncio
async def test_search_two_pages_full_results(mocker: Mocker, client: Client):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(SEARCH_TWO_PAGES_FULL_RESULTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    assert res.status_code == HTTP_200 and mock.call_count == 4
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == 2 and state.total_results == 50
    assert state.items_per_page == 25 and state.pages_count == 2


@mark.asyncio
async def test_search_more_pages_partial_results(
    mocker: Mocker, client: Client
):
    state = mocker.patch(STATE, MockState(7, 151))
    mock = mocker.patch(*get_patch(SEARCH_MORE_PAGES_PARTIAL_RESULTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    assert res.status_code == HTTP_200 and mock.call_count == 14
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == 7 and state.total_results == 151
    assert state.items_per_page == 25 and state.pages_count == 7


@mark.asyncio
async def test_search_more_pages_full_results(mocker: Mocker, client: Client):
    state = mocker.patch(STATE, MockState(7, 175))
    mock = mocker.patch(*get_patch(SEARCH_MORE_PAGES_FULL_RESULTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    assert res.status_code == HTTP_200 and mock.call_count == 14
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == 7 and state.total_results == 175
    assert state.items_per_page == 25 and state.pages_count == 7


@mark.asyncio
async def test_search_not_found(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(SEARCH_NOT_FOUND))
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
    mock = mocker.patch(*get_patch(SEARCH_QUOTA_EXCEEDED))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    errors = assert_error_json(res, HTTP_502, ScopusCode.QUOTA)
    assert errors is not None and mock.call_count == 2
    assert errors[0]["els_status"] == ScopusCode.QUOTA


@mark.asyncio
async def test_search_cancelled_error(mocker: Mocker, client: Client):
    spy = mocker.spy(ScopusResponse, "validate_search")
    mocker.patch(**STEP(MORE_CANCELLED))
    mock = mocker.patch(*get_patch(SEARCH_MORE_PAGES_PARTIAL_RESULTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    errors = assert_error_json(res, HTTP_503, CANCELLED_ERROR)

    assert mock.call_count == 7 and spy.call_count == 4
    assert errors[0]["type"] == fqn(CancelledError)
    assert errors[0]["detail"] == "any"
