import pytest
from pytest_mock import MockerFixture

from app.core.common.messages import (
    INVALID_ACCESS_TOKEN,
    MISSING_ACCESS_TOKEN,
    REQUEST_ERROR,
)
from app.core.config.config import TOKEN_HEADER
from app.framework.exceptions.http_exceptions import BaseExceptionResponse
from tests.helpers.utils import app_request
from tests.mocks.common import ANY_DICT, API_KEY, INVALID_PATTERN_VALUE, URL
from tests.mocks.fixtures import (
    INVALID_LONG_VALUE,
    INVALID_PATTERN,
    INVALID_SHORT_VALUE,
    REQUEST,
)
from tests.mocks.integration import ONE_PAGE


@pytest.mark.asyncio
async def test_success_token(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=ONE_PAGE)
    response = await app_request(URL)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_missing_token(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=ONE_PAGE)
    response = await app_request(URL, ANY_DICT)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 401
    assert not exc_response.success
    assert exc_response.code == 401
    assert exc_response.message == MISSING_ACCESS_TOKEN
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_short_invalid_token(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=ONE_PAGE)
    response = await app_request(URL, {TOKEN_HEADER: "any"})
    exc_response = BaseExceptionResponse.model_validate(response.json())
    message = REQUEST_ERROR.format(INVALID_SHORT_VALUE)

    assert response.status_code == 422
    assert not exc_response.success
    assert exc_response.code == 422
    assert exc_response.message == message
    assert exc_response.errors is not None
    assert exc_response.errors[0]["msg"] == INVALID_SHORT_VALUE


@pytest.mark.asyncio
async def test_long_invalid_token(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=ONE_PAGE)
    token = INVALID_LONG_VALUE
    response = await app_request(URL, {TOKEN_HEADER: token})
    exc_response = BaseExceptionResponse.model_validate(response.json())
    message = REQUEST_ERROR.format(INVALID_LONG_VALUE)

    assert response.status_code == 422
    assert not exc_response.success
    assert exc_response.code == 422
    assert exc_response.message == message
    assert exc_response.errors is not None
    assert exc_response.errors[0]["msg"] == INVALID_LONG_VALUE


@pytest.mark.asyncio
async def test_invalid_pattern_token(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=ONE_PAGE)
    token = INVALID_PATTERN_VALUE
    response = await app_request(URL, {TOKEN_HEADER: token})
    exc_response = BaseExceptionResponse.model_validate(response.json())
    message = REQUEST_ERROR.format(INVALID_PATTERN)

    assert response.status_code == 422
    assert not exc_response.success
    assert exc_response.code == 422
    assert exc_response.message == message
    assert exc_response.errors is not None
    assert exc_response.errors[0]["msg"] == INVALID_PATTERN


@pytest.mark.asyncio
async def test_different_token(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=ONE_PAGE)
    response = await app_request(URL, {TOKEN_HEADER: API_KEY})
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 401
    assert not exc_response.success
    assert exc_response.code == 401
    assert exc_response.message == INVALID_ACCESS_TOKEN
    assert exc_response.errors is None
