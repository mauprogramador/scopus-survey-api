import pytest
from pytest_mock import MockerFixture
from requests.exceptions import ConnectionError as ConnectError
from requests.exceptions import InvalidJSONError, Timeout

from app.core.common.messages import (
    CONNECTION_ERROR,
    CONNECTION_EXCEPTION,
    CONNECTION_TIMEOUT,
)
from app.framework.exceptions import BadGateway, GatewayTimeout
from tests.mocks.fixtures import HTTP_HELPER, SEND
from tests.mocks.unitary import HEADERS, JSONPLACEHOLDER


def test_success():
    HTTP_HELPER.mount_session(HEADERS)
    response = HTTP_HELPER.request(JSONPLACEHOLDER)
    HTTP_HELPER.close()
    assert response.status_code == 200
    assert response.json() is not None


def test_connection_timeout(mocker: MockerFixture):
    mocker.patch(SEND, side_effect=Timeout())
    HTTP_HELPER.mount_session(HEADERS)
    with pytest.raises(GatewayTimeout) as error:
        HTTP_HELPER.request(JSONPLACEHOLDER)
    HTTP_HELPER.close()
    assert error.value.status_code == 504
    assert error.value.message == CONNECTION_TIMEOUT


def test_connection_error(mocker: MockerFixture):
    mocker.patch(SEND, side_effect=ConnectError())
    HTTP_HELPER.mount_session(HEADERS)
    with pytest.raises(BadGateway) as error:
        HTTP_HELPER.request(JSONPLACEHOLDER)
    HTTP_HELPER.close()
    assert error.value.status_code == 502
    assert error.value.message == CONNECTION_ERROR


def test_connection_exception(mocker: MockerFixture):
    mocker.patch(SEND, side_effect=InvalidJSONError("any"))
    HTTP_HELPER.mount_session(HEADERS)
    with pytest.raises(BadGateway) as error:
        HTTP_HELPER.request(JSONPLACEHOLDER)
    HTTP_HELPER.close()
    message = CONNECTION_EXCEPTION.format(repr(InvalidJSONError("any")))
    assert error.value.status_code == 502
    assert error.value.message == message
