import pytest
from pytest_mock import MockerFixture

from app.core.common.messages import (
    DECODING_ERROR,
    NOT_FOUND_ERROR,
    SCOPUS_API_ERROR,
    VALIDATE_ERROR,
)
from app.core.config.scopus import API_ERRORS
from app.framework.exceptions.http_exceptions import BaseExceptionResponse
from tests.helpers.models import HeadersResponse
from tests.helpers.utils import app_request
from tests.mocks import common as data
from tests.mocks import integration as mock
from tests.mocks.fixtures import REQUEST
from tests.mocks.unitary import EXCEEDED_RESPONSE


@pytest.mark.asyncio
async def test_one_page(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ONE_PAGE)
    response = await app_request(data.URL)
    assert response.status_code == 200
    assert response.content


@pytest.mark.asyncio
async def test_two_pages(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.TWO_PAGES)
    response = await app_request(data.URL)
    assert response.status_code == 200
    assert response.content


@pytest.mark.asyncio
async def test_more_pages(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.MORE_PAGES)
    response = await app_request(data.URL)
    assert response.status_code == 200
    assert response.content


@pytest.mark.asyncio
async def test_quota_exceeded(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=EXCEEDED_RESPONSE)
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 502
    assert not exc_response.success
    assert exc_response.code == 502
    assert exc_response.message == SCOPUS_API_ERROR
    assert exc_response.errors is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("code", API_ERRORS.keys())
async def test_scopus_api_error(mocker: MockerFixture, code: int):
    if code == 429:
        mocker.patch(REQUEST, return_value=HeadersResponse())
    else:
        mocker.patch(REQUEST, return_value=data.ERROR_RESPONSES[code])
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 502
    assert not exc_response.success
    assert exc_response.code == 502
    assert exc_response.message == SCOPUS_API_ERROR
    assert exc_response.errors is not None


@pytest.mark.asyncio
async def test_empty_content(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.EMPTY_RESPONSE)
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 502
    assert not exc_response.success
    assert exc_response.code == 502
    assert exc_response.message == SCOPUS_API_ERROR
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_decoding_error(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.ANY_RESPONSE)
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 500
    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == DECODING_ERROR
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_validate_error(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.VALIDATE_ERROR_RESPONSE)
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 500
    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == VALIDATE_ERROR
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_not_found(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.NOT_FOUND)
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 404
    assert not exc_response.success
    assert exc_response.code == 404
    assert exc_response.message == NOT_FOUND_ERROR
    assert exc_response.errors is None
