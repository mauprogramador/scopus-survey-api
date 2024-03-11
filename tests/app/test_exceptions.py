import pytest
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic_core import ValidationError

from app.exceptions.handle_exceptions import (
    exception_handler,
    fastapi_validation_error_handler,
    http_exception_handler,
    pydantic_validation_error_handler,
)
from app.exceptions.http_exceptions import HttpException
from app.exceptions.http_responses import (
    BaseExceptionResponse,
    PydanticValidationExceptionResponse,
    ValidationErrorResponse,
)
from tests.data import mocks
from tests.data.utils import load_body


@pytest.mark.asyncio
async def test_handler_fastapi_request_validation_error():
    error = RequestValidationError(['any'])
    response = await fastapi_validation_error_handler(None, error)
    body = ValidationErrorResponse(**load_body(response))
    assert response.status_code == 400
    assert not body.success
    assert len(body.message)
    assert body.detail == ['any']


@pytest.mark.asyncio
async def test_handler_fastapi_response_validation_error():
    error = ResponseValidationError(['any'])
    response = await fastapi_validation_error_handler(None, error)
    body = ValidationErrorResponse(**load_body(response))
    assert response.status_code == 400
    assert not body.success
    assert len(body.message)
    assert body.detail == ['any']


@pytest.mark.asyncio
async def test_handler_pydantic_validation_error():
    error = ValidationError.from_exception_data('any', mocks.FAKE_LINE_ERRORS)
    response = await pydantic_validation_error_handler(None, error)
    body = PydanticValidationExceptionResponse(**load_body(response))
    body.detail[0]['loc'] = ()
    assert response.status_code == 500
    assert not body.success
    assert len(body.message)
    assert body.detail == error.errors()


@pytest.mark.asyncio
async def test_handler_http_exception():
    error = HttpException(400, 'any')
    response = await http_exception_handler(None, error)
    body = load_body(response)
    assert response.status_code == 400
    assert not body['success']
    assert body['message'] == 'any'


@pytest.mark.asyncio
async def test_handler_exception():
    error = Exception('any')
    response = await exception_handler(None, error)
    body = BaseExceptionResponse(**load_body(response))
    assert response.status_code == 500
    assert not body.success
    assert len(body.message)
