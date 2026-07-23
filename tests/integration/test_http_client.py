# mypy: disable-error-code="index"
import asyncio
import collections
import itertools
from json import JSONDecodeError
from typing import cast
from unittest.mock import AsyncMock, MagicMock, Mock

import aiohttp
import anyio
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.adapters.helpers.http_client import HTTPClient
from src.core.data.enums import ExcMsg
from src.core.use_cases.keyword_scouter import KeywordsScouter
from tests.conftest import assert_error_json
from tests.mocks.helpers import fqn, get_patch
from tests.mocks.integration import (
    GET_CONTENT_TYPE_ERROR,
    GET_EMPTY_RESPONSE,
    GET_JSON_DECODE_ERROR,
    GET_RATE_LIMIT,
    GET_RETRY,
    GET_SUCCESS,
    SURVEY_THREE_KEYWORDS,
)
from tests.mocks.raw import (
    COMBINATION_PARAMS,
    HTTP_200,
    HTTP_500,
    HTTP_502,
    HTTP_504,
    KEYWORDS,
    URL_COMBINATION,
)


CHAIN = fqn(KeywordsScouter, itertools.chain, "itertools")
REQUEST = fqn(aiohttp.ClientSession.request)
SLEEP = fqn(HTTPClient, asyncio.sleep, "asyncio")


def _mock_from_iterable(*_) -> tuple[str, ...]:
    return ("Python",)


@mark.asyncio
async def test_success(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(GET_SUCCESS))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3
    assert len(res.json()["result"]["combinations"]) == 3


@mark.asyncio
async def test_cancelled_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(asyncio.CancelledError("any")))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    details = assert_error_json(res, HTTP_500, ExcMsg.INTERNAL_ERROR)
    assert details[0]["type"] == fqn(RuntimeError)
    assert details[0]["message"] and mock.call_count == 3
    assert details[0]["cause"]["type"] == fqn(anyio.EndOfStream)


@mark.asyncio
async def test_timeout_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(asyncio.TimeoutError("any")))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    details = assert_error_json(res, HTTP_504, ExcMsg.CONNECTION_TIMEOUT)
    assert details[0]["type"] == fqn(asyncio.TimeoutError)
    assert details[0]["message"] and mock.call_count == 3


@mark.asyncio
async def test_client_connection_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(aiohttp.ClientConnectionError("any")))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    details = assert_error_json(res, HTTP_502, ExcMsg.CONNECTION_ERROR)
    assert details[0]["type"] == fqn(aiohttp.ClientConnectionError)
    assert details[0]["message"] and mock.call_count == 3


@mark.asyncio
async def test_uncaught_exception(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(RuntimeError("any")))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    details = assert_error_json(res, HTTP_502, ExcMsg.REQUEST_EXCEPTION)
    assert details[0]["type"] == fqn(RuntimeError)
    assert details[0]["message"] and mock.call_count == 3


@mark.asyncio
async def test_content_type_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(GET_CONTENT_TYPE_ERROR))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    details = assert_error_json(res, HTTP_502, ExcMsg.INVALID_JSON_ERROR)
    assert details[0]["type"] == fqn(aiohttp.ContentTypeError)
    assert details[0]["message"] and mock.call_count == 3


@mark.asyncio
async def test_no_data_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(GET_EMPTY_RESPONSE))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    details = assert_error_json(res, HTTP_502, ExcMsg.INVALID_JSON_ERROR)
    assert details[0]["type"] == fqn(JSONDecodeError)
    assert details[0]["message"] and mock.call_count == 3


@mark.asyncio
async def test_json_decode_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(GET_JSON_DECODE_ERROR))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    details = assert_error_json(res, HTTP_502, ExcMsg.INVALID_JSON_ERROR)
    assert details[0]["type"] == fqn(JSONDecodeError)
    assert details[0]["message"] and mock.call_count == 3


@mark.asyncio
async def test_request_retry(mocker: Mocker, client: Client):
    from_iterable = Mock(
        itertools.chain.from_iterable, side_effect=_mock_from_iterable
    )
    mocker.patch(
        CHAIN, MagicMock(itertools.chain, from_iterable=from_iterable)
    )
    new_request = AsyncMock(aiohttp.ClientResponse, side_effect=GET_RETRY)
    mock = mocker.patch(REQUEST, new_request)
    await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert mock.call_count == 3

    group_call = collections.defaultdict(list)
    for call in mock.call_args_list:
        attempt = call.kwargs["trace_request_ctx"]["current_attempt"]
        group_call[call.args[1]].append(attempt)

    assert len(group_call.keys()) == 1 and max(*group_call.values()) == 3


@mark.asyncio
async def test_retry_on_rate_limit(mocker: Mocker, client: Client):
    mock_sleep = cast(AsyncMock, getattr(client, "mock_sleep"))
    mock = mocker.patch(*get_patch(GET_RATE_LIMIT))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 4
    mock_sleep.assert_any_await(2)
    # filter retry calls = call(0)
    calls = [call for call in mock_sleep.call_args_list if call != call(0)]
    assert len(calls) == 4 * 2 + 1  # 8 req + 1 rate limit
    assert len(res.json()["result"]["combinations"]) == 3
    mock.assert_awaited()


@mark.asyncio
async def test_batch_additional_sleep(mocker: Mocker, client: Client):
    mock_sleep = cast(AsyncMock, getattr(client, "mock_sleep"))
    mocker.patch(f"{fqn(HTTPClient)}._BATCH", 5)
    mock = mocker.patch(*get_patch(SURVEY_THREE_KEYWORDS))
    mocker.patch.dict(COMBINATION_PARAMS, {"keywords": KEYWORDS[:3]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 7
    mock_sleep.assert_any_await(1.5)
    # filter retry calls = call(0)
    calls = [call for call in mock_sleep.call_args_list if call != call(0)]
    assert len(calls) == 7 * 2 + 1  # 7 req + 1 rate limit
    mock.assert_awaited()
