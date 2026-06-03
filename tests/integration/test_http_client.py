# mypy: disable-error-code="index"
from asyncio import CancelledError
from asyncio import TimeoutError as AsyncTimeoutError
from asyncio import sleep
from collections import defaultdict
from itertools import chain
from json import JSONDecodeError
from unittest.mock import AsyncMock, MagicMock, Mock

from aiohttp import (
    ClientConnectionError,
    ClientResponse,
    ClientSession,
    ContentTypeError,
)
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.adapters.helpers.http_client import HTTPClient
from src.core.common.types import RateStrategy
from src.core.data.enums import ExcMsg
from src.core.config.config import LOG
from src.core.data.quota_results_handler import QuotaResultsHandler
from src.core.domain.factory import make_aggregator
from src.core.use_cases.keyword_combination_finder import (
    KeywordCombinationFinder,
)
from tests.conftest import assert_error_json
from tests.mocks.helpers import (
    MockState,
    fqn,
    get_patch,
    mock_from_iterable,
)
from tests.mocks.integration import (
    GET_CONTENT_TYPE_ERROR,
    GET_EMPTY_RESPONSE,
    GET_JSON_DECODE_ERROR,
    GET_RATE_LIMIT,
    GET_RETRY,
    GET_STRATEGY,
    GET_SUCCESS,
)
from tests.mocks.raw import (
    COMBINATION_PARAMS,
    HTTP_200,
    HTTP_502,
    HTTP_503,
    HTTP_504,
    LOG_MOCK,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_SEARCH,
)


STATE = fqn(make_aggregator, QuotaResultsHandler)
CHAIN = fqn(KeywordCombinationFinder, chain)
LOG_STRATEGY = fqn(HTTPClient, LOG_MOCK.strategy)
REQUEST = fqn(ClientSession.request)
SLEEP = fqn(HTTPClient, sleep)


@mark.asyncio
async def test_success(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(GET_SUCCESS))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3
    assert len(res.json()["data"]["combinations"]) == 3


@mark.asyncio
async def test_cancelled_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(CancelledError("any")))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_503, ExcMsg.CANCELLED_ERROR)
    assert errors[0]["type"] == fqn(CancelledError)
    assert errors[0]["detail"] == "any" and mock.call_count == 3


@mark.asyncio
async def test_timeout_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(AsyncTimeoutError("any")))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_504, ExcMsg.CONNECTION_TIMEOUT)
    assert errors[0]["type"] == fqn(AsyncTimeoutError)
    assert errors[0]["detail"] == "any" and mock.call_count == 3


@mark.asyncio
async def test_client_connection_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(ClientConnectionError("any")))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_502, ExcMsg.CONNECTION_ERROR)
    assert errors[0]["type"] == fqn(ClientConnectionError)
    assert errors[0]["detail"] == "any" and mock.call_count == 3


@mark.asyncio
async def test_uncaught_exception(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(RuntimeError("any")))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_502, ExcMsg.REQUEST_EXCEPTION)
    assert errors[0]["type"] == fqn(RuntimeError)
    assert errors[0]["detail"] == "any" and mock.call_count == 3


@mark.asyncio
async def test_content_type_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(GET_CONTENT_TYPE_ERROR))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_502, ExcMsg.INVALID_JSON_ERROR)
    assert len(errors) == 2 and mock.call_count == 3
    assert errors[0]["type"] == fqn(ContentTypeError)
    assert errors[0]["detail"] and errors[1]["body"] is not None


@mark.asyncio
async def test_no_data_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(GET_EMPTY_RESPONSE))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_502, ExcMsg.INVALID_JSON_ERROR)
    assert len(errors) == 2 and mock.call_count == 3
    assert errors[0]["type"] == fqn(JSONDecodeError)
    assert errors[0]["detail"] and errors[1]["body"] is not None


@mark.asyncio
async def test_json_decode_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(GET_JSON_DECODE_ERROR))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_502, ExcMsg.INVALID_JSON_ERROR)
    assert len(errors) == 2 and mock.call_count == 3
    assert errors[0]["type"] == fqn(JSONDecodeError)
    assert errors[0]["detail"] and errors[1]["body"] is not None


@mark.asyncio
async def test_request_retry(mocker: Mocker, client: Client):
    from_iterable = Mock(chain.from_iterable, side_effect=mock_from_iterable)
    mocker.patch(CHAIN, MagicMock(chain, from_iterable=from_iterable))
    new_request = AsyncMock(ClientResponse, side_effect=GET_RETRY)
    mock = mocker.patch(REQUEST, new_request)
    await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert mock.call_count == 3
    mock.assert_called()

    group_call = defaultdict(list)
    for call in mock.call_args_list:
        attempt = call.kwargs["trace_request_ctx"]["current_attempt"]
        group_call[call.args[1]].append(attempt)

    assert len(group_call.keys()) == 1 and max(*group_call.values()) == 3


@mark.asyncio
async def test_retry_on_rate_limit(mocker: Mocker, client: Client):
    spy = mocker.patch(SLEEP, wraps=sleep)
    mock = mocker.patch(*get_patch(GET_RATE_LIMIT))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert spy.call_args_list[0].args[0] == 2
    assert spy.call_count == 2  # +1 close
    assert res.status_code == HTTP_200 and mock.call_count == 4
    assert len(res.json()["data"]["combinations"]) == 3
    spy.assert_awaited()
    mock.assert_awaited()


@mark.asyncio
async def test_update_strategy_and_additional_sleep(
    mocker: Mocker, client: Client
):
    state = mocker.patch(STATE, MockState(5, 113))
    spy_sleep = mocker.patch(SLEEP, wraps=sleep)
    spy_log = mocker.patch(LOG_STRATEGY, wraps=LOG.strategy)
    mock = mocker.patch(*get_patch(GET_STRATEGY))

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 10
    strategy: RateStrategy = spy_log.call_args_list[1].args[0]
    assert strategy.rate == 7.5 and strategy.backoff == 2.2
    assert spy_sleep.call_count == 2  # +1 close

    spy_sleep.assert_awaited()
    spy_log.assert_called()
    mock.assert_awaited()

    assert len(state.entry) == 5 and state.total_results == 113
    assert state.items_per_page == 25 and state.pages_count == 5
