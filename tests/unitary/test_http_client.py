from asyncio import CancelledError, Semaphore
from asyncio import TimeoutError as AsyncTimeoutError
from asyncio import gather, sleep
from json import JSONDecodeError
from unittest.mock import AsyncMock

from aiohttp import (
    ClientConnectionError,
    ClientResponse,
    ClientSession,
    ContentTypeError,
)
from aiolimiter import AsyncLimiter
from pytest import fixture, mark, raises
from pytest_asyncio import fixture as async_fixture
from pytest_mock import MockerFixture as Mocker

from src.adapters.helpers.http_client import HTTPClient
from src.core.common.error_messages import (
    CONNECTION_ERROR,
    CONNECTION_TIMEOUT,
    INVALID_JSON_ERROR,
    REQUEST_EXCEPTION,
    SCOPUS_API_ERROR,
)
from src.core.common.types import RateStrategy
from src.core.config.config import LOG
from src.core.domain.http_exceptions import (
    BadGateway,
    GatewayTimeout,
    ScopusAPIError,
)
from tests.conftest import assert_http_error
from tests.mocks.helpers import fqn, get_patch, http_patch
from tests.mocks.raw import HTTP_200, HTTP_502, HTTP_504, LOG_MOCK
from tests.mocks.unitary import (
    GET_CONTENT_TYPE_ERROR,
    GET_EMPTY_RESPONSE,
    GET_JSON_DECODE_ERROR,
    GET_RATE_LIMIT,
    GET_RETRY,
    GET_SUCCESS,
)

LOG_STRATEGY = fqn(HTTPClient, LOG_MOCK.strategy)
REQUEST = fqn(ClientSession.request)
SLEEP = fqn(HTTPClient, sleep)


@async_fixture(scope="module", loop_scope="module", name="client")
async def http_client_instance():
    http_client = HTTPClient()
    yield http_client
    await http_client.close()


@fixture(autouse=True)
def mock_telemetry(mocker: Mocker):
    mocker.patch(*http_patch(AsyncLimiter.__aenter__))
    mocker.patch(*http_patch(AsyncLimiter.__aexit__))
    mocker.patch(*http_patch(Semaphore.__aenter__))
    mocker.patch(*http_patch(Semaphore.__aexit__))


@mark.asyncio(loop_scope="module")
async def test_success(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(GET_SUCCESS))
    bundle = await client.request("any")
    assert bundle.code == HTTP_200
    assert bundle.data is not None and bundle.headers is not None
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_cancelled_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(CancelledError("any")))
    with raises(CancelledError) as info:
        await client.request("any")
    assert info.value.args[0] == "any"
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_timeout_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(AsyncTimeoutError("any")))
    with raises(GatewayTimeout) as info:
        await client.request("any")
    assert_http_error(info, HTTP_504, CONNECTION_TIMEOUT)
    assert info.value.errors[0]["type"] == fqn(AsyncTimeoutError)
    assert info.value.errors[0]["detail"] == "any"
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_client_connection_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(ClientConnectionError("any")))
    with raises(BadGateway) as info:
        await client.request("any")
    assert_http_error(info, HTTP_502, CONNECTION_ERROR)
    assert info.value.errors[0]["type"] == fqn(ClientConnectionError)
    assert info.value.errors[0]["detail"] == "any"
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_uncaught_exception(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(RuntimeError("any")))
    with raises(BadGateway) as info:
        await client.request("any")
    assert_http_error(info, HTTP_502, REQUEST_EXCEPTION)
    assert info.value.errors[0]["type"] == fqn(RuntimeError)
    assert info.value.errors[0]["detail"] == "any"
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_content_type_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(GET_CONTENT_TYPE_ERROR))
    with raises(ScopusAPIError) as info:
        await client.request("any")
    assert_http_error(info, HTTP_502, INVALID_JSON_ERROR)
    assert info.value.errors[0]["els_status"] == INVALID_JSON_ERROR
    assert info.value.errors[0]["code_error"] == SCOPUS_API_ERROR
    assert info.value.errors[1]["type"] == fqn(ContentTypeError)
    assert info.value.errors[1]["detail"] == "any"
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_no_data_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(GET_EMPTY_RESPONSE))
    with raises(ScopusAPIError) as info:
        await client.request("any")
    assert_http_error(info, HTTP_502, INVALID_JSON_ERROR)
    assert info.value.errors[0]["els_status"] == INVALID_JSON_ERROR
    assert info.value.errors[0]["code_error"] == SCOPUS_API_ERROR
    assert info.value.errors[1]["type"] == fqn(JSONDecodeError)
    assert info.value.errors[1]["detail"]
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_json_decode_error(mocker: Mocker, client: HTTPClient):
    mock = mocker.patch(*get_patch(GET_JSON_DECODE_ERROR))
    with raises(ScopusAPIError) as info:
        await client.request("any")
    assert_http_error(info, HTTP_502, INVALID_JSON_ERROR)
    assert info.value.errors[0]["els_status"] == INVALID_JSON_ERROR
    assert info.value.errors[0]["code_error"] == SCOPUS_API_ERROR
    assert info.value.errors[1]["type"] == fqn(JSONDecodeError)
    assert info.value.errors[1]["detail"]
    mock.assert_awaited_once()


@mark.asyncio(loop_scope="module")
async def test_request_retry(mocker: Mocker, client: HTTPClient):
    new_request = AsyncMock(ClientResponse, side_effect=GET_RETRY)
    mock = mocker.patch(REQUEST, new_request)
    bundle = await client.request("any")
    assert bundle.code == HTTP_200 and mock.call_count == len(GET_RETRY)
    assert bundle.data is not None and bundle.headers is not None


@mark.asyncio(loop_scope="module")
async def test_retry_on_rate_limit(mocker: Mocker, client: HTTPClient):
    spy = mocker.patch(SLEEP, wraps=sleep)
    mock = mocker.patch(*get_patch(GET_RATE_LIMIT))
    bundle = await client.request("any")
    assert spy.call_args_list[0].args[0] == 2
    assert bundle.code == HTTP_200 and mock.call_count == 2
    assert bundle.data is not None and bundle.headers is not None
    spy.assert_awaited_once()
    mock.assert_awaited()


@mark.asyncio(loop_scope="module")
async def test_update_strategy(mocker: Mocker, client: HTTPClient):
    spy = mocker.patch(LOG_STRATEGY, wraps=LOG.strategy)
    await client.update_strategy(411)
    strategy: RateStrategy = spy.call_args_list[0].args[0]
    assert strategy.rate == 6.0 and strategy.backoff == 3.0
    spy.assert_called_once()


@mark.asyncio(loop_scope="module")
async def test_additional_sleep(mocker: Mocker, client: HTTPClient):
    spy = mocker.patch(SLEEP, wraps=sleep)
    mock = mocker.patch(*get_patch(GET_SUCCESS))
    await client.update_strategy(2000)
    tasks = [client.request("any") for _ in range(5)]
    await gather(*tasks)
    assert spy.call_count == 5 and mock.call_count == 5
    spy.assert_awaited()
    mock.assert_awaited()
