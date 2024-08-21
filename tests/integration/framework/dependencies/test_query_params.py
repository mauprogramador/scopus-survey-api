import pytest
from pytest_mock import MockerFixture

from app.core.common.messages import (
    INVALID_KEYWORD,
    INVALID_KEYWORDS_LENGTH,
    MISSING_API_KEY,
    MISSING_KEYWORDS,
    REQUEST_ERROR,
)
from app.framework.exceptions.http_exceptions import BaseExceptionResponse
from tests.helpers.utils import app_request
from tests.mocks import common as data
from tests.mocks import fixtures as fix
from tests.mocks import integration as mock


@pytest.mark.asyncio
async def test_success_params(mocker: MockerFixture):
    mocker.patch(fix.REQUEST, side_effect=mock.ONE_PAGE)
    response = await app_request(data.URL)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_missing_api_key(mocker: MockerFixture):
    mocker.patch(fix.REQUEST, side_effect=mock.ONE_PAGE)
    response = await app_request(mock.NO_PARAMS_URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 401
    assert not exc_response.success
    assert exc_response.code == 401
    assert exc_response.message == MISSING_API_KEY
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_short_invalid_api_key(mocker: MockerFixture):
    mocker.patch(fix.REQUEST, side_effect=mock.ONE_PAGE)
    response = await app_request(f"{mock.API_KEY_URL}any")
    exc_response = BaseExceptionResponse.model_validate(response.json())
    message = REQUEST_ERROR.format(fix.INVALID_SHORT_VALUE)

    assert response.status_code == 422
    assert not exc_response.success
    assert exc_response.code == 422
    assert exc_response.message == message
    assert exc_response.errors is not None
    assert exc_response.errors[0]["msg"] == fix.INVALID_SHORT_VALUE


@pytest.mark.asyncio
async def test_long_invalid_api_key(mocker: MockerFixture):
    mocker.patch(fix.REQUEST, side_effect=mock.ONE_PAGE)
    url = f"{mock.API_KEY_URL}{data.INVALID_LONG_VALUE}"
    response = await app_request(url)
    exc_response = BaseExceptionResponse.model_validate(response.json())
    message = REQUEST_ERROR.format(fix.INVALID_LONG_VALUE)

    assert response.status_code == 422
    assert not exc_response.success
    assert exc_response.code == 422
    assert exc_response.message == message
    assert exc_response.errors is not None
    assert exc_response.errors[0]["msg"] == fix.INVALID_LONG_VALUE


@pytest.mark.asyncio
async def test_invalid_pattern_api_key(mocker: MockerFixture):
    mocker.patch(fix.REQUEST, side_effect=mock.ONE_PAGE)
    url = f"{mock.API_KEY_URL}{data.INVALID_PATTERN_VALUE}"
    response = await app_request(url)
    exc_response = BaseExceptionResponse.model_validate(response.json())
    message = REQUEST_ERROR.format(fix.INVALID_PATTERN)

    assert response.status_code == 422
    assert not exc_response.success
    assert exc_response.code == 422
    assert exc_response.message == message
    assert exc_response.errors is not None
    assert exc_response.errors[0]["msg"] == fix.INVALID_PATTERN


@pytest.mark.asyncio
async def test_missing_keywords(mocker: MockerFixture):
    mocker.patch(fix.REQUEST, side_effect=mock.ONE_PAGE)
    response = await app_request(mock.NO_KEYWORDS_URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 422
    assert not exc_response.success
    assert exc_response.code == 422
    assert exc_response.message == MISSING_KEYWORDS
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_invalid_keywords_length(mocker: MockerFixture):
    mocker.patch(fix.REQUEST, side_effect=mock.ONE_PAGE)
    response = await app_request(f"{mock.KEYWORDS_URL}any")
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 422
    assert not exc_response.success
    assert exc_response.code == 422
    assert exc_response.message == INVALID_KEYWORDS_LENGTH
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_short_invalid_keywords(mocker: MockerFixture):
    mocker.patch(fix.REQUEST, side_effect=mock.ONE_PAGE)
    response = await app_request(f"{mock.KEYWORDS_URL}a,b")
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 422
    assert not exc_response.success
    assert exc_response.code == 422
    assert exc_response.message == INVALID_KEYWORD
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_long_invalid_keywords(mocker: MockerFixture):
    mocker.patch(fix.REQUEST, side_effect=mock.ONE_PAGE)
    response = await app_request(f"{mock.KEYWORDS_URL}key1,{'a' * 125}")
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 422
    assert not exc_response.success
    assert exc_response.code == 422
    assert exc_response.message == INVALID_KEYWORD
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_blank_space_keywords(mocker: MockerFixture):
    mocker.patch(fix.REQUEST, side_effect=mock.ONE_PAGE)
    response = await app_request(f"{mock.KEYWORDS_URL}, ,     ")
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 422
    assert not exc_response.success
    assert exc_response.code == 422
    assert exc_response.message == INVALID_KEYWORD
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_invalid_keywords_pattern(mocker: MockerFixture):
    mocker.patch(fix.REQUEST, side_effect=mock.ONE_PAGE)
    response = await app_request(f"{mock.KEYWORDS_URL}f@3f!sH%3P,f@3f!sH%3P")
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 422
    assert not exc_response.success
    assert exc_response.code == 422
    assert exc_response.message == INVALID_KEYWORD
    assert exc_response.errors is None
