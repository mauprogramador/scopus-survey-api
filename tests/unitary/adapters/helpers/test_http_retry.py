from pytest import fixture, raises
from pytest_mock import MockerFixture
from requests.exceptions import ConnectionError as ConnectError
from requests.exceptions import InvalidJSONError, Timeout

from src.adapters.helpers.http_retry import HTTPRetry
from src.core.common.messages import (
    CONNECTION_ERROR,
    CONNECTION_EXCEPTION,
    CONNECTION_TIMEOUT,
)
from src.core.domain.http_exceptions import BadGateway, GatewayTimeout
from tests.mocks.fixtures import HTTP_RETRY, SEND

JSONPLACEHOLDER = "https://jsonplaceholder.typicode.com/users/1"


@fixture(scope="module", name="http_session")
def http_client_session():
    HTTP_RETRY.mount_session({"Content-Type": "application/json"})
    yield HTTP_RETRY
    HTTP_RETRY.close()


def test_success(http_session: HTTPRetry):
    response = http_session.request(JSONPLACEHOLDER)
    assert response.status_code == 200
    assert response.json() is not None


def test_connection_timeout(http_session: HTTPRetry, mocker: MockerFixture):
    mocker.patch(SEND, side_effect=Timeout("any"))
    with raises(GatewayTimeout) as exc:
        http_session.request(JSONPLACEHOLDER)
    assert exc.value.status_code == 504
    assert exc.value.message == CONNECTION_TIMEOUT
    assert exc.value.errors and isinstance(exc.value.errors, list)
    assert exc.value.errors[0]["type"].count("Timeout")


def test_connection_error(http_session: HTTPRetry, mocker: MockerFixture):
    mocker.patch(SEND, side_effect=ConnectError("any"))
    with raises(BadGateway) as exc:
        http_session.request(JSONPLACEHOLDER)
    assert exc.value.status_code == 502
    assert exc.value.message == CONNECTION_ERROR
    assert exc.value.errors and isinstance(exc.value.errors, list)
    assert exc.value.errors[0]["type"].count("ConnectionError")


def test_connection_exception(http_session: HTTPRetry, mocker: MockerFixture):
    mocker.patch(SEND, side_effect=InvalidJSONError("any"))
    with raises(BadGateway) as exc:
        http_session.request(JSONPLACEHOLDER)
    assert exc.value.status_code == 502
    assert exc.value.message == CONNECTION_EXCEPTION
    assert exc.value.errors and isinstance(exc.value.errors, list)
    assert exc.value.errors[0]["type"].count("InvalidJSONError")
