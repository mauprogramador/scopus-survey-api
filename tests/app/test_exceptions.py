import pytest
from fastapi import Response
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic_core import ValidationError

from app.core.exceptions import ScopusApiError
from app.framework.exceptions.handle_exceptions import ExceptionHandler
from app.framework.exceptions.http_exceptions import HTTPException
from app.framework.exceptions.http_responses import (
    BaseExceptionResponse,
    PydanticValidationExceptionResponse,
    ValidationErrorResponse,
)
from tests.data import mocks
from tests.data.utils import load_body


@pytest.mark.asyncio
async def test_handler_fastapi_request_validation_error():
    error = RequestValidationError(['any'])
    handler = ExceptionHandler()
    response = await handler.fastapi_validation_error_handler(None, error)
    body = ValidationErrorResponse(**load_body(response))
    assert response.status_code == 400
    assert not body.success
    assert len(body.message)
    assert body.detail == ['any']


@pytest.mark.asyncio
async def test_handler_fastapi_response_validation_error():
    error = ResponseValidationError(['any'])
    handler = ExceptionHandler()
    response = await handler.fastapi_validation_error_handler(None, error)
    body = ValidationErrorResponse(**load_body(response))
    assert response.status_code == 400
    assert not body.success
    assert len(body.message)
    assert body.detail == ['any']


@pytest.mark.asyncio
async def test_handler_pydantic_validation_error():
    error = ValidationError.from_exception_data('any', mocks.FAKE_LINE_ERRORS)
    handler = ExceptionHandler()
    response = await handler.pydantic_validation_error_handler(None, error)
    body = PydanticValidationExceptionResponse(**load_body(response))
    body.detail[0]['loc'] = ()
    assert response.status_code == 500
    assert not body.success
    assert len(body.message)
    assert body.detail == error.errors()


@pytest.mark.asyncio
async def test_handler_http_exception():
    error = HTTPException(400, 'any')
    handler = ExceptionHandler()
    response = await handler.http_exception_handler(None, error)
    body = load_body(response)
    assert response.status_code == 400
    assert body == 'any'


@pytest.mark.asyncio
async def test_handler_scopus_api_error():
    response = Response('any', 500)
    error = ScopusApiError(response)
    handler = ExceptionHandler()
    response = await handler.scopus_api_error_handler(None, error)
    json_body = load_body(response)
    assert response.status_code == 422
    assert not json_body['success']
    assert json_body['message'] == error.message
    assert json_body['detail'] == error.detail
    assert json_body['body'] == error.body


@pytest.mark.asyncio
async def test_handler_exception():
    error = Exception('any')
    handler = ExceptionHandler()
    response = await handler.exception_handler(None, error)
    body = BaseExceptionResponse(**load_body(response))
    assert response.status_code == 500
    assert not body.success
    assert len(body.message)
