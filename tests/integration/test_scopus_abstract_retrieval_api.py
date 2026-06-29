# mypy: disable-error-code="index"
import asyncio
from unittest.mock import MagicMock, PropertyMock

from httpx import AsyncClient as Client
from pydantic import ValidationError
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from src.adapters.helpers.scopus_response import validate_abstract_response
from src.core.config.scopus import QUOTA_ERROR_CODE
from src.core.data.enums import ExcMsg
from src.core.data.quota_results_handler import QuotaResultsHandler
from src.core.domain.factory import make_aggregator
from src.utils.progress_bar import ProgressBar
from tests.conftest import assert_error_json
from tests.mocks.errors import (
    SCOPUS_API_QUOTA_ERROR,
    TASKS_CANCELLED_ERROR,
    TASKS_COMMON_ERROR,
    TASKS_HTTP_ERROR,
)
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
    HTTP_400,
    HTTP_500,
    HTTP_502,
    SEARCH_PARAMS,
    URL_SEARCH,
)


STATE = fqn(make_aggregator, QuotaResultsHandler)
ABSTRACT_RES = fqn(ScopusAbstractRetrievalAPI, validate_abstract_response)
STEP = Patch(ScopusAbstractRetrievalAPI, ProgressBar.step, "ProgressBar")


@mark.asyncio
async def test_retrieve_one_partial_abstract(mocker: Mocker, client: Client):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(RETRIEVE_ONE_PARTIAL_ABSTRACT))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 2
    df = load_csv_from_response(res)
    assert df.shape[0] == 1
    assert df["Authors"].iloc[0] == "any_author"
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
    assert df["Authors"].iloc[0] == "any_author_1, any_author_2"
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
    "res_mock,total",
    [
        (ABSTRACT_EXACT_QUOTA_ONE_RESULT, 1),
        (ABSTRACT_EXACT_QUOTA_TWO_RESULTS, 2),
        (ABSTRACT_EXACT_QUOTA_MORE_RESULTS, 7),
    ],
    ids=["One res_mock", "Two results", "More results"],
)
async def test_retrieve_exact_quota_limit(
    mocker: Mocker, client: Client, res_mock: list[MagicMock], total: int
):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(res_mock))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == total + 1
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == state.total_results == total
    assert state.total_abstracts == len(state.abstracts) == total


@mark.asyncio
@mark.parametrize(
    "res_mock,count,total",
    [
        (ABSTRACT_NO_QUOTA_TWO_RESULTS, 1, 2),
        (ABSTRACT_NO_QUOTA_MORE_RESULTS, 4, 7),
    ],
    ids=["Two results", "More results"],
)
async def test_retrieve_insufficient_quota(
    mocker: Mocker,
    client: Client,
    res_mock: list[MagicMock],
    count: int,
    total: int,
):
    state = mocker.patch(STATE, MockState())
    mock = mocker.patch(*get_patch(res_mock))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == (count + 1)
    assert load_csv_from_response(res).shape[0] == 1
    assert len(state.entry) == total and state.total_results == total
    assert state.total_abstracts == len(state.abstracts) == count


@mark.asyncio
async def test_retrieve_quota_exceed(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(ABSTRACT_QUOTA_EXCEEDED))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    details = assert_error_json(res, HTTP_502, trans(SCOPUS_API_QUOTA_ERROR))
    assert details is not None and mock.call_count == 2
    assert details[0]["error_code"] == QUOTA_ERROR_CODE


@mark.asyncio
async def test_retrieve_no_tasks(mocker: Mocker, client: Client):
    mocker.patch(
        f"{fqn(QuotaResultsHandler)}.abstracts_to_fetch_range",
        PropertyMock(return_value=range(0)),
    )
    mock = mocker.patch(*get_patch(RETRIEVE_MORE_ABSTRACTS))

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    details = assert_error_json(res, HTTP_500, ExcMsg.INTERNAL_ERROR)
    assert mock.call_count == 2 and details is None


@mark.asyncio
async def test_retrieve_http_error(mocker: Mocker, client: Client):
    spy = mocker.patch(ABSTRACT_RES, wraps=validate_abstract_response)
    mock = mocker.patch(*get_patch(RETRIEVE_MORE_ABSTRACTS))
    mocker.patch(**STEP(TASKS_HTTP_ERROR))

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    details = assert_error_json(res, HTTP_400, ExcMsg.INTERNAL_ERROR)
    # _get_abstract has more CPU executions like model_dump
    assert mock.call_count == 8 and spy.call_count == 7
    assert details[0]["type"] == fqn(ValueError)
    assert details[0]["message"] == "any"


@mark.asyncio
async def test_retrieve_cancelled_error(mocker: Mocker, client: Client):
    spy = mocker.patch(ABSTRACT_RES, wraps=validate_abstract_response)
    mock = mocker.patch(*get_patch(RETRIEVE_MORE_ABSTRACTS))
    mocker.patch(**STEP(TASKS_CANCELLED_ERROR))

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    details = assert_error_json(res, HTTP_500, ExcMsg.CANCELLED_ERROR)

    # TaskGroup swallows CancelledError
    assert mock.call_count == 8 and spy.call_count == 7
    assert details[0]["type"] == fqn(asyncio.CancelledError)
    assert details[0]["message"] == "any"


@mark.asyncio
async def test_retrieve_operational_error(mocker: Mocker, client: Client):
    spy = mocker.patch(ABSTRACT_RES, wraps=validate_abstract_response)
    mock = mocker.patch(*get_patch(RETRIEVE_MORE_ABSTRACTS))
    mocker.patch(**STEP(TASKS_COMMON_ERROR))

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    details = assert_error_json(res, HTTP_500, ExcMsg.CANCELLED_ERROR)

    # _get_abstract has more CPU executions like model_dump
    assert mock.call_count == 8 and spy.call_count in (6, 7)
    assert details[0]["type"] == fqn(ValidationError)
    assert details[0]["message"] is not None
