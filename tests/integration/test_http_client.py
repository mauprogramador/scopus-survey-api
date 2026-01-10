# mypy: disable-error-code="index"
from asyncio import CancelledError
from asyncio import TimeoutError as AsyncTimeoutError
from asyncio import sleep
from collections import defaultdict
from itertools import chain
from json import JSONDecodeError
from unittest.mock import AsyncMock, MagicMock, Mock

from aiohttp import ClientConnectionError, ClientSession, ContentTypeError
from aiohttp_retry import RetryClient
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.adapters.helpers.http_client import HTTPClient
from src.core.common.error_messages import (
    CANCELLED_ERROR,
    CONNECTION_ERROR,
    CONNECTION_TIMEOUT,
    INVALID_JSON_ERROR,
    REQUEST_EXCEPTION,
    SCOPUS_API_ERROR,
)
from src.core.common.types import RateStrategy
from src.core.config.config import LOG
from src.core.use_cases.keyword_combination_finder import (
    KeywordCombinationFinder,
)
from tests.conftest import assert_error_json
from tests.mocks.helpers import fqn, mock_from_iterable
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
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_SEARCH,
)

CHAIN = fqn(KeywordCombinationFinder, chain)
LOG_STRATEGY = fqn(HTTPClient, "LOG.strategy")
REQUEST = fqn(ClientSession.request)
SLEEP = fqn(HTTPClient, sleep)
GET = fqn(RetryClient.get)


@mark.asyncio
async def test_success(mocker: Mocker, client: Client):
    mock = mocker.patch(GET, new=AsyncMock(side_effect=GET_SUCCESS))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3
    assert len(res.json()["data"]["combinations"]) == 3


@mark.asyncio
async def test_cancelled_error(mocker: Mocker, client: Client):
    mock = mocker.patch(GET, new=AsyncMock(side_effect=CancelledError("any")))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_503, CANCELLED_ERROR)
    assert errors[0]["type"] == fqn(CancelledError)
    assert errors[0]["detail"] == "any" and mock.call_count == 3


@mark.asyncio
async def test_timeout_error(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET, new=AsyncMock(side_effect=AsyncTimeoutError("any"))
    )
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_504, CONNECTION_TIMEOUT)
    assert errors[0]["type"] == fqn(AsyncTimeoutError)
    assert errors[0]["detail"] == "any" and mock.call_count == 3


@mark.asyncio
async def test_client_connection_error(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET, new=AsyncMock(side_effect=ClientConnectionError("any"))
    )
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_502, CONNECTION_ERROR)
    assert errors[0]["type"] == fqn(ClientConnectionError)
    assert errors[0]["detail"] == "any" and mock.call_count == 3


@mark.asyncio
async def test_uncaught_exception(mocker: Mocker, client: Client):
    mock = mocker.patch(GET, new=AsyncMock(side_effect=RuntimeError("any")))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_502, REQUEST_EXCEPTION)
    assert errors[0]["type"] == fqn(RuntimeError)
    assert errors[0]["detail"] == "any" and mock.call_count == 3


@mark.asyncio
async def test_content_type_error(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET, new=AsyncMock(return_value=GET_CONTENT_TYPE_ERROR)
    )
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_502, SCOPUS_API_ERROR)
    assert errors[0]["els_status"] == INVALID_JSON_ERROR
    assert errors[0]["code_error"] == SCOPUS_API_ERROR
    assert errors[1]["type"] == fqn(ContentTypeError)
    assert errors[1]["detail"] == "any" and mock.call_count == 3


@mark.asyncio
async def test_no_data_error(mocker: Mocker, client: Client):
    mock = mocker.patch(GET, new=AsyncMock(return_value=GET_EMPTY_RESPONSE))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_502, SCOPUS_API_ERROR)
    assert errors[0]["els_status"] == INVALID_JSON_ERROR
    assert errors[0]["code_error"] == SCOPUS_API_ERROR
    assert errors[1]["type"] == fqn(JSONDecodeError)
    assert errors[1]["detail"] and mock.call_count == 3


@mark.asyncio
async def test_json_decode_error(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(return_value=GET_JSON_DECODE_ERROR),
    )
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_502, SCOPUS_API_ERROR)
    assert errors[0]["els_status"] == INVALID_JSON_ERROR
    assert errors[0]["code_error"] == SCOPUS_API_ERROR
    assert errors[1]["type"] == fqn(JSONDecodeError)
    assert errors[1]["detail"] and mock.call_count == 3


@mark.asyncio
async def test_request_retry(mocker: Mocker, client: Client):
    mocker.patch(
        CHAIN,
        new=MagicMock(from_iterable=Mock(side_effect=mock_from_iterable)),
    )
    mock = mocker.patch(REQUEST, new=AsyncMock(side_effect=GET_RETRY))
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
    mock = mocker.patch(GET, new=AsyncMock(side_effect=GET_RATE_LIMIT))
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
    spy_sleep = mocker.patch(SLEEP, wraps=sleep)
    spy_log = mocker.patch(LOG_STRATEGY, wraps=LOG.strategy)
    mock = mocker.patch(GET, new=AsyncMock(side_effect=GET_STRATEGY))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    strategy: RateStrategy = spy_log.call_args_list[2].args[0]
    assert res.status_code == HTTP_200 and mock.call_count == 118
    assert strategy.rate == 7.5 and strategy.backoff == 2.2
    assert spy_sleep.call_count == 4  # +1 close
    spy_sleep.assert_awaited()
    spy_log.assert_called()
    mock.assert_awaited()
