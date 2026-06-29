import asyncio
from json import JSONDecodeError
from unittest.mock import AsyncMock

import aiohttp
from pytest import fixture, mark, raises
from pytest_asyncio import fixture as async_fixture
from pytest_mock import MockerFixture as Mocker

from src.adapters.helpers.http_client import HTTPClient
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import (
    BadGateway,
    BadGatewayContent,
    GatewayTimeout,
)
from tests.conftest import LIMITER, SEMAPHORE, assert_http_error
from tests.mocks.helpers import MockAsyncContext, fqn, get_patch
from tests.mocks.raw import HTTP_200, HTTP_502, HTTP_504
from tests.mocks.unitary import (
    GET_CONTENT_TYPE_ERROR,
    GET_EMPTY_RESPONSE,
    GET_JSON_DECODE_ERROR,
    GET_RATE_LIMIT,
    GET_RETRY,
    GET_SUCCESS,
)


REQUEST = fqn(aiohttp.ClientSession.request)
SLEEP = fqn(HTTPClient, asyncio.sleep, "asyncio")
TIMEOUT = fqn(HTTPClient, aiohttp.ClientTimeout, "aiohttp")


@async_fixture(name="client")
async def http_client_instance():
    http_client = HTTPClient()
    yield http_client
    await http_client.close()


@fixture(autouse=True, name="mock_sleep")
def mock_concurrent_utils(mocker: Mocker):
    mocker.patch(LIMITER, new_callable=MockAsyncContext)
    mocker.patch(SEMAPHORE, new_callable=MockAsyncContext)
    mock = mocker.patch(SLEEP, new_callable=AsyncMock)
    yield mock


@mark.asyncio
async def test_success(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(GET_SUCCESS))
    bundle = await client.api_call("any")
    assert bundle.code == HTTP_200
    assert bundle.data is not None and bundle.headers is not None
    mock.assert_awaited_once()


@mark.asyncio
async def test_cancelled_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(asyncio.CancelledError("any")))
    with raises(asyncio.CancelledError) as info:
        await client.api_call("any")
    assert info.value.args[0] == "any"
    mock.assert_awaited_once()


@mark.asyncio
async def test_timeout_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(asyncio.TimeoutError("any")))
    with raises(GatewayTimeout) as info:
        await client.api_call("any")
    assert_http_error(info, HTTP_504, ExcMsg.CONNECTION_TIMEOUT)
    assert info.value.details[0]["type"] == fqn(asyncio.TimeoutError)
    assert info.value.details[0]["message"] == "any"
    mock.assert_awaited_once()


@mark.asyncio
async def test_client_connection_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(aiohttp.ClientConnectionError("any")))
    with raises(BadGateway) as info:
        await client.api_call("any")
    assert_http_error(info, HTTP_502, ExcMsg.CONNECTION_ERROR)
    assert info.value.details[0]["type"] == fqn(aiohttp.ClientConnectionError)
    assert info.value.details[0]["message"] == "any"
    mock.assert_awaited_once()


@mark.asyncio
async def test_uncaught_exception(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(RuntimeError("any")))
    with raises(BadGateway) as info:
        await client.api_call("any")
    assert_http_error(info, HTTP_502, ExcMsg.REQUEST_EXCEPTION)
    assert info.value.details[0]["type"] == fqn(RuntimeError)
    assert info.value.details[0]["message"] == "any"
    mock.assert_awaited_once()


@mark.asyncio
async def test_content_type_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(GET_CONTENT_TYPE_ERROR))
    with raises(BadGatewayContent) as info:
        await client.api_call("any")
    assert_http_error(info, HTTP_502, ExcMsg.INVALID_JSON_ERROR)
    assert len(info.value.details) == 2
    assert info.value.details[0]["type"] == fqn(aiohttp.ContentTypeError)
    assert info.value.details[0]["message"] == "any"
    assert info.value.details[1]["raw_body"] is not None
    assert info.value.details[1]["message"] == "any"
    assert info.value.details[1]["status_code"] == 400
    mock.assert_awaited_once()


@mark.asyncio
async def test_no_data_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(GET_EMPTY_RESPONSE))
    with raises(BadGatewayContent) as info:
        await client.api_call("any")
    assert_http_error(info, HTTP_502, ExcMsg.INVALID_JSON_ERROR)
    assert info.value.details[0]["type"] == fqn(JSONDecodeError)
    assert info.value.details[0]["message"] is not None
    assert info.value.details[1]["raw_body"] is not None
    assert info.value.details[1]["message"] == "Expecting value"
    assert info.value.details[1]["doc"] == "Scopus JSON"
    mock.assert_awaited_once()


@mark.asyncio
async def test_json_decode_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(GET_JSON_DECODE_ERROR))
    with raises(BadGatewayContent) as info:
        await client.api_call("any")
    assert_http_error(info, HTTP_502, ExcMsg.INVALID_JSON_ERROR)
    assert info.value.details[0]["type"] == fqn(JSONDecodeError)
    assert info.value.details[0]["message"] is not None
    assert info.value.details[1]["raw_body"] is not None
    assert info.value.details[1]["message"] == "any"
    assert info.value.details[1]["doc"] == "any"
    mock.assert_awaited_once()


@mark.asyncio
async def test_request_retry(mocker: Mocker, client: HTTPClient):
    new_request = AsyncMock(aiohttp.ClientResponse, side_effect=GET_RETRY)
    mock = mocker.patch(REQUEST, new_request)
    bundle = await client.api_call("any")
    assert bundle.code == HTTP_200 and mock.call_count == len(GET_RETRY)
    assert bundle.data is not None and bundle.headers is not None


@mark.asyncio
async def test_retry_on_rate_limit(
    mocker: Mocker, client: HTTPClient, mock_sleep: AsyncMock
):
    spy_clear = mocker.spy(asyncio.Event, "clear")
    spy_set = mocker.spy(asyncio.Event, "set")
    mock = mocker.patch(*get_patch(GET_RATE_LIMIT))

    bundle = await client.api_call("any")
    assert bundle.code == HTTP_200 and mock.call_count == 2
    assert bundle.data is not None and bundle.headers is not None

    mock_sleep.assert_awaited()
    mock_sleep.assert_any_await(2)
    mock_sleep.reset_mock()

    spy_clear.assert_called_once()
    spy_set.assert_called_once()
    mock.assert_awaited()


@mark.asyncio
async def test_batch_additional_sleep(
    mocker: Mocker, client: HTTPClient, mock_sleep: AsyncMock
):
    mocker.patch(f"{fqn(HTTPClient)}._BATCH", 5)
    spy_clear = mocker.spy(asyncio.Event, "clear")
    spy_set = mocker.spy(asyncio.Event, "set")
    mock = mocker.patch(*get_patch([GET_SUCCESS] * 7))

    bundles = [await client.api_call("any") for _ in range(7)]
    assert len(bundles) == 7 and mock.call_count == 7

    mock_sleep.assert_awaited()
    assert mock_sleep.call_args_list[9].args[0] == 1.5
    # Sleep: n * (api_call + _request) + _track_batch
    assert mock_sleep.call_count == 7 * 2 + 1

    spy_clear.assert_called_once()
    spy_set.assert_called_once()
    mock.assert_awaited()
