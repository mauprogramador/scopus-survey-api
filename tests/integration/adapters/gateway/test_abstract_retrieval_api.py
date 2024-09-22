import pytest
from pytest_mock import MockerFixture

from app.core.common.messages import (
    ABSTRACT_API_ERROR,
    DECODING_ERROR,
    VALIDATE_ERROR,
)
from app.core.config.scopus import API_ERRORS
from app.framework.exceptions.http_exceptions import BaseExceptionResponse
from tests.helpers.models import HeadersResponse
from tests.helpers.utils import app_request, content_response
from tests.mocks import common as data
from tests.mocks import integration as mock
from tests.mocks.fixtures import REQUEST


@pytest.mark.asyncio
async def test_one_abstract(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ONE_ROW)
    response = await app_request(data.URL)
    content = content_response(response)
    assert response.status_code == 200
    assert response.content and content.shape == (1, 11)


@pytest.mark.asyncio
async def test_two_abstracts(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.TWO_ROWS)
    response = await app_request(data.URL)
    content = content_response(response)
    assert response.status_code == 200
    assert response.content and content.shape == (2, 11)


@pytest.mark.asyncio
async def test_more_abstracts(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.MORE_ROWS)
    response = await app_request(data.URL)
    content = content_response(response)
    assert response.status_code == 200
    assert response.content and content.shape == (7, 11)


@pytest.mark.asyncio
@pytest.mark.parametrize("code", API_ERRORS.keys())
async def test_scopus_api_error(mocker: MockerFixture, code: int):
    if code == 429:
        responses = [*mock.uni.ONE_PAGE, HeadersResponse()]
        mocker.patch(REQUEST, side_effect=responses)
    else:
        responses = [*mock.uni.ONE_PAGE, data.ERROR_RESPONSES[code]]
        mocker.patch(REQUEST, side_effect=responses)
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 502
    assert not exc_response.success
    assert exc_response.code == 502
    assert exc_response.message == ABSTRACT_API_ERROR
    assert exc_response.errors is not None


@pytest.mark.asyncio
async def test_empty_content(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.EMPTY_RESPONSE)
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 502
    assert not exc_response.success
    assert exc_response.code == 502
    assert exc_response.message == ABSTRACT_API_ERROR
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_decoding_error(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.DECODING_ERROR_RESPONSE)
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 500
    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == DECODING_ERROR
    assert exc_response.errors is None


@pytest.mark.asyncio
async def test_validate_error(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.VALIDATE_ERROR_RESPONSE)
    response = await app_request(data.URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 500
    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == VALIDATE_ERROR
    assert exc_response.errors is None
