# mypy: disable-error-code="index"
from asyncio import CancelledError
from unittest.mock import MagicMock

from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from src.adapters.helpers.scopus_response import ScopusResponse
from src.core.config.scopus import QUOTA_ERROR_CODE
from src.core.data.enums import Column, ExcMsg
from src.core.data.quota_results_handler import QuotaResultsHandler
from src.core.domain.factory import make_aggregator
from src.utils.progress_bar import ProgressBar
from tests.conftest import assert_error_json
from tests.mocks.errors import MORE_CANCELLED, SCOPUS_API_QUOTA_ERROR
from tests.mocks.helpers import (
    MockState,
    Patch,
    fqn,
    get_patch,
    load_csv_from_response,
    trans,
)
from tests.mocks.integration import (
    ABSTRACT_EXACT_QUOTA_MORE_RESULTS,
    ABSTRACT_EXACT_QUOTA_ONE_RESULT,
    ABSTRACT_EXACT_QUOTA_TWO_RESULTS,
    ABSTRACT_NO_QUOTA_MORE_RESULTS,
    ABSTRACT_NO_QUOTA_TWO_RESULTS,
    ABSTRACT_QUOTA_EXCEEDED,
    RETRIEVE_MORE_ABSTRACTS,
    RETRIEVE_ONE_ABSTRACT_AUTHORS,
    RETRIEVE_ONE_ABSTRACT_FULL,
    RETRIEVE_ONE_PARTIAL_ABSTRACT,
    RETRIEVE_TWO_ABSTRACTS,
)
from tests.mocks.raw import (
    HTTP_200,
    HTTP_502,
    HTTP_503,
    SEARCH_PARAMS,
    URL_SEARCH,
)


STATE = fqn(make_aggregator, QuotaResultsHandler)
STEP = Patch(ScopusAbstractRetrievalAPI, ProgressBar(0).step)


@mark.asyncio
async def test_retrieve_one_partial_abstract(mocker: Mocker, client: Client):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(RETRIEVE_ONE_PARTIAL_ABSTRACT))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 2
    df = load_csv_from_response(res)
    assert df.shape[0] == 1
    assert df[Column.AUTHORS].iloc[0] == "any_author"
    assert len(state.entry) == state.total_results == 1
    assert state.total_abstracts == len(state.abstracts) == 1


@mark.asyncio
async def test_retrieve_one_abstract_authors(mocker: Mocker, client: Client):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(RETRIEVE_ONE_ABSTRACT_AUTHORS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 2
    df = load_csv_from_response(res)
    assert df.shape[0] == 1
    assert df[Column.AUTHORS].iloc[0] == "any_author_1, any_author_2"
    assert len(state.entry) == state.total_results == 1
    assert state.total_abstracts == len(state.abstracts) == 1


@mark.asyncio
async def test_retrieve_one_abstract_full(mocker: Mocker, client: Client):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(RETRIEVE_ONE_ABSTRACT_FULL))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 2
    df = load_csv_from_response(res)
    assert df.shape[0] == 1
    assert df["Abstract"].iloc[0] == "any_abstract"
    assert len(state.entry) == state.total_results == 1
    assert state.total_abstracts == len(state.abstracts) == 1


@mark.asyncio
async def test_retrieve_two_abstracts(mocker: Mocker, client: Client):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(RETRIEVE_TWO_ABSTRACTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == state.total_results == 2
    assert state.total_abstracts == len(state.abstracts) == 2


@mark.asyncio
async def test_retrieve_more_abstracts(mocker: Mocker, client: Client):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(RETRIEVE_MORE_ABSTRACTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 8
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == 7 and state.total_results == 7
    assert state.total_abstracts == len(state.abstracts) == 7


@mark.asyncio
@mark.parametrize(
    "response,total",
    [
        (ABSTRACT_EXACT_QUOTA_ONE_RESULT, 1),
        (ABSTRACT_EXACT_QUOTA_TWO_RESULTS, 2),
        (ABSTRACT_EXACT_QUOTA_MORE_RESULTS, 7),
    ],
    ids=["One result", "Two results", "More results"],
)
async def test_retrieve_exact_quota_limit(
    mocker: Mocker, client: Client, response: list[MagicMock], total: int
):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(response))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == total + 1
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == state.total_results == total
    assert state.total_abstracts == len(state.abstracts) == total


@mark.asyncio
@mark.parametrize(
    "response,count,total",
    [
        (ABSTRACT_NO_QUOTA_TWO_RESULTS, 1, 2),
        (ABSTRACT_NO_QUOTA_MORE_RESULTS, 4, 7),
    ],
    ids=["Two results", "More results"],
)
async def test_retrieve_insufficient_quota(
    mocker: Mocker,
    client: Client,
    response: list[MagicMock],
    count: int,
    total: int,
):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(response))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == (count + 1)
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == total and state.total_results == total
    assert state.total_abstracts == len(state.abstracts) == count


@mark.asyncio
async def test_retrieve_quota_exceed(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(ABSTRACT_QUOTA_EXCEEDED))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    errors = assert_error_json(res, HTTP_502, trans(SCOPUS_API_QUOTA_ERROR))
    assert errors is not None and mock.call_count == 3
    assert errors[0]["els_status"] == QUOTA_ERROR_CODE


@mark.asyncio
async def test_retrieve_cancelled_error(mocker: Mocker, client: Client):
    spy = mocker.spy(ScopusResponse, "validate_abstract")
    mocker.patch(**STEP(MORE_CANCELLED))
    mock = mocker.patch(*get_patch(RETRIEVE_MORE_ABSTRACTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    errors = assert_error_json(res, HTTP_503, ExcMsg.CANCELLED_ERROR)

    assert mock.call_count == 8 and spy.call_count == 4
    assert errors[0]["type"] == fqn(CancelledError)
    assert errors[0]["detail"] == "any"
