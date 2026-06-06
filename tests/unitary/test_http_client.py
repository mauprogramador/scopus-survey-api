import asyncio
from json import JSONDecodeError
from unittest.mock import AsyncMock

import aiohttp
import aiolimiter
from pytest import fixture, mark, raises
from pytest_asyncio import fixture as async_fixture
from pytest_mock import MockerFixture as Mocker

from src.adapters.helpers.http_client import HTTPClient
from src.core.common.types import RateStrategy
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import (
    BadGateway,
    BadGatewayContent,
    GatewayTimeout,
)
from src.utils import logger
from tests.conftest import assert_http_error
from tests.mocks.helpers import fqn, get_patch, http_patch
from tests.mocks.raw import HTTP_200, HTTP_502, HTTP_504
from tests.mocks.unitary import (
    GET_CONTENT_TYPE_ERROR,
    GET_EMPTY_RESPONSE,
    GET_JSON_DECODE_ERROR,
    GET_RATE_LIMIT,
    GET_RETRY,
    GET_SUCCESS,
)


LOG_STRATEGY = fqn(HTTPClient, logger.strategy, "logger")
REQUEST = fqn(aiohttp.ClientSession.request)
SLEEP = fqn(HTTPClient, asyncio.sleep, "asyncio")


@async_fixture(scope="module", loop_scope="module", name="client")
async def http_client_instance():
    http_client = HTTPClient()
    yield http_client
    await http_client.close()


@fixture(autouse=True)
def mock_telemetry(mocker: Mocker):
    mocker.patch(*http_patch(aiolimiter.AsyncLimiter.__aenter__))
    mocker.patch(*http_patch(aiolimiter.AsyncLimiter.__aexit__))
    mocker.patch(*http_patch(asyncio.Semaphore.__aenter__))
    mocker.patch(*http_patch(asyncio.Semaphore.__aexit__))


@mark.asyncio(loop_scope="module")
async def test_success(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(GET_SUCCESS))
    bundle = await client.request("any")
    assert bundle.code == HTTP_200
    assert bundle.data is not None and bundle.headers is not None
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_cancelled_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(asyncio.CancelledError("any")))
    with raises(asyncio.CancelledError) as info:
        await client.request("any")
    assert info.value.args[0] == "any"
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_timeout_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(asyncio.TimeoutError("any")))
    with raises(GatewayTimeout) as info:
        await client.request("any")
    assert_http_error(info, HTTP_504, ExcMsg.CONNECTION_TIMEOUT)
    assert info.value.errors[0]["type"] == fqn(asyncio.TimeoutError)
    assert info.value.errors[0]["message"] == "any"
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_client_connection_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(aiohttp.ClientConnectionError("any")))
    with raises(BadGateway) as info:
        await client.request("any")
    assert_http_error(info, HTTP_502, ExcMsg.CONNECTION_ERROR)
    assert info.value.errors[0]["type"] == fqn(aiohttp.ClientConnectionError)
    assert info.value.errors[0]["message"] == "any"
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_uncaught_exception(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(RuntimeError("any")))
    with raises(BadGateway) as info:
        await client.request("any")
    assert_http_error(info, HTTP_502, ExcMsg.REQUEST_EXCEPTION)
    assert info.value.errors[0]["type"] == fqn(RuntimeError)
    assert info.value.errors[0]["message"] == "any"
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_content_type_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(GET_CONTENT_TYPE_ERROR))
    with raises(BadGatewayContent) as info:
        await client.request("any")
    assert_http_error(info, HTTP_502, ExcMsg.INVALID_JSON_ERROR)
    assert len(info.value.errors) == 2
    assert info.value.errors[0]["type"] == fqn(aiohttp.ContentTypeError)
    assert info.value.errors[0]["message"] == "any"
    assert info.value.errors[1]["raw_body"] is not None
    assert info.value.errors[1]["message"] == "any"
    assert info.value.errors[1]["status_code"] == 400
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_no_data_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(GET_EMPTY_RESPONSE))
    with raises(BadGatewayContent) as info:
        await client.request("any")
    assert_http_error(info, HTTP_502, ExcMsg.INVALID_JSON_ERROR)
    assert info.value.errors[0]["type"] == fqn(JSONDecodeError)
    assert info.value.errors[0]["message"] is not None
    assert info.value.errors[1]["raw_body"] is not None
    assert info.value.errors[1]["message"] == "Expecting value"
    assert info.value.errors[1]["doc"] == "Scopus JSON"
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_json_decode_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(GET_JSON_DECODE_ERROR))
    with raises(BadGatewayContent) as info:
        await client.request("any")
    assert_http_error(info, HTTP_502, ExcMsg.INVALID_JSON_ERROR)
    assert info.value.errors[0]["type"] == fqn(JSONDecodeError)
    assert info.value.errors[0]["message"] is not None
    assert info.value.errors[1]["raw_body"] is not None
    assert info.value.errors[1]["message"] == "any"
    assert info.value.errors[1]["doc"] == "any"
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_request_retry(mocker: Mocker, client: HTTPClient):
    new_request = AsyncMock(aiohttp.ClientResponse, side_effect=GET_RETRY)
    mock = mocker.patch(REQUEST, new_request)
    bundle = await client.request("any")
    assert bundle.code == HTTP_200 and mock.call_count == len(GET_RETRY)
    assert bundle.data is not None and bundle.headers is not None


@mark.asyncio(loop_scope="module")
async def test_retry_on_rate_limit(mocker: Mocker, client: HTTPClient):
    spy = mocker.patch(SLEEP, wraps=asyncio.sleep)
    mock = mocker.patch(*get_patch(GET_RATE_LIMIT))
    bundle = await client.request("any")
    assert spy.call_args_list[0].args[0] == 2
    assert bundle.code == HTTP_200 and mock.call_count == 2
    assert bundle.data is not None and bundle.headers is not None
    spy.assert_awaited_once()
    mock.assert_awaited()


@mark.asyncio(loop_scope="module")
async def test_update_strategy(mocker: Mocker, client: HTTPClient):
    spy = mocker.patch(LOG_STRATEGY, wraps=logger.strategy)
    await client.update_strategy(411)
    strategy: RateStrategy = spy.call_args_list[0].args[0]
    assert strategy.rate == 6.0 and strategy.backoff == 3.0
    spy.assert_called_once()


@mark.asyncio(loop_scope="module")
async def test_additional_sleep(mocker: Mocker, client: HTTPClient):
    spy = mocker.patch(SLEEP, wraps=asyncio.sleep)
    mock = mocker.patch(*get_patch(GET_SUCCESS))
    await client.update_strategy(2000)
    tasks = [client.request("any") for _ in range(5)]
    await asyncio.gather(*tasks)
    assert spy.call_count == 5 and mock.call_count == 5
    spy.assert_awaited()
    mock.assert_awaited()
