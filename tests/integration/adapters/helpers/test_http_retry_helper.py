import pytest
from pytest_mock import MockerFixture
from requests.exceptions import ConnectionError as ConnectError
from requests.exceptions import InvalidJSONError, Timeout

from app.core.common.messages import (
    CONNECTION_ERROR,
    CONNECTION_EXCEPTION,
    CONNECTION_TIMEOUT,
)
from app.framework.exceptions.http_exceptions import BaseExceptionResponse
from tests.helpers.utils import app_request
from tests.mocks import common as data
from tests.mocks.fixtures import SEND
from tests.mocks.integration import ONE_PAGE


@pytest.mark.asyncio
async def test_success(mocker: MockerFixture):
    mocker.patch(SEND, side_effect=ONE_PAGE)
    response = await app_request(data.URL)
    assert response.status_code == 200
    assert response.content


@pytest.mark.asyncio
async def test_connection_timeout(mocker: MockerFixture):
    mocker.patch(SEND, side_effect=Timeout())
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 504
    assert not exc_response.success
    assert exc_response.code == 504
    assert exc_response.message == CONNECTION_TIMEOUT
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_connection_error(mocker: MockerFixture):
    mocker.patch(SEND, side_effect=ConnectError())
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 502
    assert not exc_response.success
    assert exc_response.code == 502
    assert exc_response.message == CONNECTION_ERROR
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_connection_exception(mocker: MockerFixture):
    mocker.patch(SEND, side_effect=InvalidJSONError("any"))
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())
    message = CONNECTION_EXCEPTION.format(repr(InvalidJSONError("any")))

    assert response.status_code == 502
    assert not exc_response.success
    assert exc_response.code == 502
    assert exc_response.message == message
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_response_status_error(mocker: MockerFixture):
    mocker.patch(SEND, return_value=data.ERROR_RESPONSES[500])
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 502
    assert not exc_response.success
    assert exc_response.code == 502
    assert response.status_code == 502
    assert not exc_response.success
    assert exc_response.code == 502
