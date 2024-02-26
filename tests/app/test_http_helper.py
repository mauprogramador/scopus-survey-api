import pytest
from pytest_mock import MockerFixture
from requests.exceptions import ConnectionError as ConnectError
from requests.exceptions import Timeout

from app.gateway.http_helper import HttpHelper
from tests.data import mocks
from tests.data.request import app_request


@pytest.mark.asyncio
async def test_unit_http_helper_success():
    response = HttpHelper.make_request(mocks.FAKE_API_URL, {})
    assert response.status_code == 200
    assert len(response.json())


@pytest.mark.asyncio
async def test_http_helper_timeout(mocker: MockerFixture):
    mocker.patch(mocks.SESSION_SEND, side_effect=Timeout())
    response = await app_request(mocks.URL)
    assert response.status_code == 424
    assert not response.json()['success']
    assert response.json()['message'] == mocks.CONNECTION_TIMEOUT


@pytest.mark.asyncio
async def test_http_helper_connect_error(mocker: MockerFixture):
    mocker.patch(mocks.SESSION_SEND, side_effect=ConnectError())
    response = await app_request(mocks.URL)
    assert response.status_code == 424
    assert not response.json()['success']
    assert response.json()['message'] == mocks.CONNECTION_ERROR


@pytest.mark.asyncio
async def test_http_helper_exception(mocker: MockerFixture):
    mocker.patch(mocks.SESSION_SEND, side_effect=Exception('any'))
    response = await app_request(mocks.URL)
    assert response.status_code == 424
    assert not response.json()['success']
    assert response.json()['message'] == mocks.CONNECTION_EXCEPTION
