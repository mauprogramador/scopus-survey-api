import pytest
from pytest_mock import MockerFixture
from requests.exceptions import ConnectionError as ConnectError
from requests.exceptions import Timeout

from app.exceptions import ScopusApiError
from app.gateway.api_config import ApiConfig
from app.gateway.http_helper import HttpHelper
from tests.data import mocks
from tests.data.request import app_request
from tests.data.utils import assert_csv_response


@pytest.mark.asyncio
async def test_unit_http_helper_success():
    response = HttpHelper().make_request(mocks.FAKE_LINK, {})
    assert response.status_code == 200
    assert len(response.json())


@pytest.mark.asyncio
async def test_http_helper_search_timeout(mocker: MockerFixture):
    mocker.patch(mocks.RANGE, return_value=range(2, 3))
    mocker.patch(mocks.SESSION_SEND, side_effect=Timeout())
    response = await app_request(mocks.URL)
    assert response.status_code == 424
    assert not response.json()['success']
    assert response.json()['message'] == mocks.CONNECTION_TIMEOUT


@pytest.mark.asyncio
async def test_http_helper_scraping_timeout(mocker: MockerFixture):
    fake_returns = [mocks.FAKE_RESPONSE_200, Timeout()]
    mocker.patch(mocks.RANGE, return_value=range(2, 3))
    mocker.patch(mocks.SESSION_SEND, side_effect=fake_returns)
    response = await app_request(mocks.URL)
    assert_csv_response(response)


@pytest.mark.asyncio
async def test_http_helper_search_connect_error(mocker: MockerFixture):
    mocker.patch(mocks.RANGE, return_value=range(2, 3))
    mocker.patch(mocks.SESSION_SEND, side_effect=ConnectError())
    response = await app_request(mocks.URL)
    assert response.status_code == 424
    assert not response.json()['success']
    assert response.json()['message'] == mocks.CONNECTION_ERROR


@pytest.mark.asyncio
async def test_http_helper_scraping_connect_error(mocker: MockerFixture):
    fake_returns = [mocks.FAKE_RESPONSE_200, ConnectError()]
    mocker.patch(mocks.RANGE, return_value=range(2, 3))
    mocker.patch(mocks.SESSION_SEND, side_effect=fake_returns)
    response = await app_request(mocks.URL)
    assert_csv_response(response)


@pytest.mark.asyncio
async def test_http_helper_search_exception(mocker: MockerFixture):
    mocker.patch(mocks.RANGE, return_value=range(2, 3))
    mocker.patch(mocks.SESSION_SEND, side_effect=Exception('any'))
    response = await app_request(mocks.URL)
    assert response.status_code == 424
    assert not response.json()['success']
    assert response.json()['message'] == mocks.CONNECTION_EXCEPTION


@pytest.mark.asyncio
async def test_http_helper_scraping_exception(mocker: MockerFixture):
    fake_returns = [mocks.FAKE_RESPONSE_200, Exception('any')]
    mocker.patch(mocks.RANGE, return_value=range(2, 3))
    mocker.patch(mocks.SESSION_SEND, side_effect=fake_returns)
    response = await app_request(mocks.URL)
    assert_csv_response(response)


@pytest.mark.asyncio
async def test_http_helper_request_retry(mocker: MockerFixture):
    mocker.patch(mocks.SESSION_SEND, side_effect=mocks.FAKE_RETRY)
    sleep_spy = mocker.patch(mocks.SLEEP)
    response = HttpHelper().make_request(mocks.FAKE_LINK, {})
    assert response.status_code == 200
    assert sleep_spy.call_count == 2
    sleep_spy.assert_called()


@pytest.mark.asyncio
async def test_http_helper_search_request_retry(mocker: MockerFixture):
    fake_returns = [Timeout(), Timeout(), Timeout()]
    mocker.patch(mocks.SESSION_SEND, side_effect=fake_returns)
    sleep_spy = mocker.patch(mocks.SLEEP)
    response = await app_request(mocks.URL)
    assert response.status_code == 424
    assert not response.json()['success']
    assert response.json()['message'] == mocks.CONNECTION_TIMEOUT
    assert sleep_spy.call_count == 2
    sleep_spy.assert_called()


@pytest.mark.asyncio
async def test_http_helper_scraping_request_retry(mocker: MockerFixture):
    fake_returns = [mocks.FAKE_RESPONSE_200, Timeout(), Timeout(), Timeout()]
    mocker.patch(mocks.SESSION_SEND, side_effect=fake_returns)
    sleep_spy = mocker.patch(mocks.SLEEP)
    response = await app_request(mocks.URL)
    assert_csv_response(response)
    assert sleep_spy.call_count == 2
    sleep_spy.assert_called()


@pytest.mark.asyncio
@pytest.mark.parametrize('code', mocks.FAKE_HTTP_RESPONSES.keys())
async def test_http_helper_search_status_error(
    mocker: MockerFixture, code: int
):
    mocker.patch(mocks.RANGE, return_value=range(2, 3))
    mocker.patch(
        mocks.SESSION_SEND, return_value=mocks.FAKE_HTTP_RESPONSES[code]
    )
    response = await app_request(mocks.URL)
    data = ScopusApiError(**response.json())
    assert response.status_code == 422
    assert not data.success
    assert data.message == mocks.INVALID_RESPONSE
    assert data.status.startswith(f'{code}')
    assert data.detail == ApiConfig.RESPONSES.get(code, 'null')


@pytest.mark.asyncio
@pytest.mark.parametrize('code', mocks.FAKE_HTTP_RESPONSES.keys())
async def test_http_helper_scraping_status_error(
    mocker: MockerFixture, code: int
):
    fake_returns = [mocks.FAKE_RESPONSE_200, mocks.FAKE_HTTP_RESPONSES[code]]
    mocker.patch(mocks.RANGE, return_value=range(2, 3))
    mocker.patch(mocks.SESSION_SEND, side_effect=fake_returns)
    response = await app_request(mocks.URL)
    assert_csv_response(response)
