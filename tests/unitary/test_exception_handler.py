# mypy: disable-error-code="index"
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic import ValidationError
from pytest import mark
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.data.enums import ExcMsg
from src.framework.middleware import exception_handler as handler
from tests.conftest import assert_error_json
from tests.mocks.errors import (
    FASTAPI_HTTP_EXCEPTION,
    HTTP_ERROR,
    PYDANTIC_VALIDATION_ERROR,
    RATE_LIMIT_ERROR,
    REQUEST_VALIDATION_ERROR,
    RESPONSE_VALIDATION_ERROR,
    SCOPUS_API_ERROR,
    STARLETTE_HTTP_EXCEPTION,
)
from tests.mocks.helpers import fqn, trans
from tests.mocks.raw import (
    HTTP_400,
    HTTP_422,
    HTTP_429,
    HTTP_500,
    HTTP_502,
    REQUEST,
)


@mark.asyncio
async def test_custom_http_error():
    res = await handler.custom_http_error(REQUEST, HTTP_ERROR)
    errors = assert_error_json(res, HTTP_400, ExcMsg.UNEXPECTED_ERROR)
    assert errors[0]["type"] == fqn(ValueError)
    assert errors[0]["message"] == "any"


@mark.asyncio
async def test_scopus_api_error():
    res = await handler.scopus_api_error(REQUEST, SCOPUS_API_ERROR)
    errors = assert_error_json(res, HTTP_502, trans(SCOPUS_API_ERROR))
    assert errors[0]["status_code"] == HTTP_500
    assert errors[0]["error_code"] == "ANY"
    assert errors[1]["any"] == "any"


@mark.asyncio
async def test_starlette_http_exception():
    error = STARLETTE_HTTP_EXCEPTION
    res = await handler.starlette_http_exception(REQUEST, error)
    errors = assert_error_json(res, HTTP_500, trans(error))
    assert errors[0]["type"] == fqn(StarletteHTTPException)
    assert errors[0]["message"] == "any"


@mark.asyncio
async def test_fastapi_http_exception():
    error = FASTAPI_HTTP_EXCEPTION
    res = await handler.starlette_http_exception(REQUEST, error)
    errors = assert_error_json(res, HTTP_500, trans(error))
    assert errors[0]["type"] == fqn(FastAPIHTTPException)
    assert errors[0]["message"] == "any"


@mark.asyncio
async def test_fastapi_request_validation_error():
    error = REQUEST_VALIDATION_ERROR
    res = await handler.fastapi_validation_error(REQUEST, error)
    errors = assert_error_json(res, HTTP_422, trans(error))
    assert errors[0]["type"] == fqn(RequestValidationError)
    assert errors[0]["message"] == "any"
    assert errors[1]["msg"] == "any"


@mark.asyncio
async def test_fastapi_response_validation_error():
    error = RESPONSE_VALIDATION_ERROR
    res = await handler.fastapi_validation_error(REQUEST, error)
    errors = assert_error_json(res, HTTP_500, trans(error))
    assert errors[0]["type"] == fqn(ResponseValidationError)
    assert errors[0]["message"] == "any"
    assert errors[1]["msg"] == "any"


@mark.asyncio
async def test_pydantic_validation_error():
    error = PYDANTIC_VALIDATION_ERROR
    res = await handler.pydantic_validation_error(REQUEST, error)
    errors = assert_error_json(res, HTTP_500, trans(error))
    assert errors[0]["type"] == fqn(ValidationError)
    assert errors[0]["message"] == "Field required"
    assert errors[1]["type"] == "missing"
    assert errors[1]["msg"] == "Field required"
    assert errors[1]["input"] == "any"


@mark.asyncio
async def test_rate_limit_error():
    res = await handler.rate_limit_error(REQUEST, RATE_LIMIT_ERROR)
    errors = assert_error_json(res, HTTP_429, trans(RATE_LIMIT_ERROR))
    assert errors[0]["type"] == fqn(RateLimitExceeded)
    assert errors[0]["message"] == "any"
    assert errors[1]["status_code"] == 429 and errors[1]["limit"] is not None
    assert errors[1]["rate"] == RATE_LIMIT_ERROR.detail
