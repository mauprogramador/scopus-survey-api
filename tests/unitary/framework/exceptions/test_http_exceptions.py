from http import HTTPStatus

import pytest
from fastapi.encoders import jsonable_encoder

from app.core.common.messages import (
    PYDANTIC_ERROR,
    REQUEST_ERROR,
    RESPONSE_ERROR,
    UNEXPECTED_ERROR,
)
from app.core.config.scopus import API_ERRORS, NULL
from tests.helpers.utils import exception_response
from tests.mocks import fixtures as fix
from tests.mocks.common import ANY_DICT
from tests.mocks.unitary import EMPTY_REQUEST


@pytest.mark.asyncio
async def test_starlette_http_exception():
    error = fix.STARLETTE_HTTP_EXCEPTION
    response = await fix.HANDLER.starlette_http_exception(EMPTY_REQUEST, error)
    exc_response = exception_response(response)

    assert response.status_code == 500
    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == "any"
    assert not exc_response.errors


@pytest.mark.asyncio
async def test_fastapi_http_exception():
    error = fix.FASTAPI_HTTP_EXCEPTION
    response = await fix.HANDLER.fastapi_http_exception(EMPTY_REQUEST, error)
    exc_response = exception_response(response)

    assert response.status_code == 500
    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == "any"
    assert not exc_response.errors


@pytest.mark.asyncio
async def test_fastapi_request_validation_error():
    error = fix.REQUEST_VALIDATION_ERROR
    response = await fix.HANDLER.request_validation_error(EMPTY_REQUEST, error)
    exc_response = exception_response(response)

    assert response.status_code == 422
    assert not exc_response.success
    assert exc_response.code == 422
    assert exc_response.message == REQUEST_ERROR.format(NULL)
    assert exc_response.errors == [ANY_DICT]


@pytest.mark.asyncio
async def test_fastapi_response_validation_error():
    error = fix.RESPONSE_VALIDATION_ERROR
    response = await fix.HANDLER.response_validation_error(
        EMPTY_REQUEST, error
    )
    exc_response = exception_response(response)

    assert response.status_code == 500
    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == RESPONSE_ERROR.format(NULL)
    assert exc_response.errors == [ANY_DICT]


@pytest.mark.asyncio
async def test_pydantic_validation_error():
    error = fix.PYDANTIC_VALIDATION_ERROR
    response = await fix.HANDLER.pydantic_validation_error(
        EMPTY_REQUEST, error
    )
    exc_response = exception_response(response)
    message = PYDANTIC_ERROR.format(error.error_count(), error.title)

    assert response.status_code == 500
    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == message
    assert exc_response.errors == jsonable_encoder(error.errors())


@pytest.mark.asyncio
async def test_http_exception():
    error = fix.HTTP_EXCEPTION
    response = await fix.HANDLER.http_exception(EMPTY_REQUEST, error)
    exc_response = exception_response(response)

    assert response.status_code == 400
    assert not exc_response.success
    assert exc_response.code == 400
    assert exc_response.message == "any"
    assert not exc_response.errors


@pytest.mark.asyncio
async def test_application_error():
    error = fix.APPLICATION_ERROR
    response = await fix.HANDLER.application_error(EMPTY_REQUEST, error)
    exc_response = exception_response(response)

    assert response.status_code == error.code
    assert not exc_response.success
    assert exc_response.code == error.code
    assert exc_response.message == error.message
    assert not exc_response.errors


@pytest.mark.asyncio
async def test_scopus_api_error():
    error = fix.SEARCH_API_ERROR
    response = await fix.HANDLER.application_error(EMPTY_REQUEST, error)
    exc_response = exception_response(response)
    status = f"{500} {HTTPStatus(500).phrase}"

    assert response.status_code == error.code
    assert not exc_response.success
    assert exc_response.code == error.code
    assert exc_response.message == error.message
    assert exc_response.errors[0]["status"] == status
    assert exc_response.errors[0]["api_error"] == API_ERRORS.get(500)
    assert exc_response.errors[0]["content"] == ANY_DICT


@pytest.mark.asyncio
async def test_common_exception():
    error = fix.COMMON_EXCEPTION
    response = await fix.HANDLER.common_exception(EMPTY_REQUEST, error)
    exc_response = exception_response(response)

    assert response.status_code == 500
    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == UNEXPECTED_ERROR.format(repr(error))
    assert not exc_response.errors
