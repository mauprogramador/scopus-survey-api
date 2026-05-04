# mypy: disable-error-code="index"
from pytest import mark

from src.core.config.scopus import SCOPUS_ERRORS
from src.framework.middleware.exception_handler import ExceptionHandler
from tests.conftest import assert_error_json
from tests.mocks.errors import (
    FASTAPI_HTTP_EXCEPTION,
    HTTP_ERROR,
    PYDANTIC_UNDEFINED_ERROR,
    PYDANTIC_VALIDATION_ERROR,
    RATE_LIMIT_ERROR,
    REQUEST_VALIDATION_ERROR,
    RESPONSE_VALIDATION_ERROR,
    RESPONSE_VALIDATION_EXCEPTION_ERROR,
    SCOPUS_API_ERROR,
    STARLETTE_HTTP_EXCEPTION,
)
from tests.mocks.helpers import fqn
from tests.mocks.raw import (
    HTTP_400,
    HTTP_422,
    HTTP_429,
    HTTP_500,
    HTTP_502,
    REQUEST,
)


HANDLER = ExceptionHandler()


@mark.asyncio
async def test_custom_http_error():
    res = await HANDLER.custom_http_error(REQUEST, HTTP_ERROR)
    errors = assert_error_json(res, HTTP_400, "any")
    assert errors[0]["type"] == fqn(ValueError)
    assert errors[0]["detail"] == "any"


@mark.asyncio
async def test_scopus_api_error():
    res = await HANDLER.scopus_api_error(REQUEST, SCOPUS_API_ERROR)
    errors = assert_error_json(res, HTTP_502, "any")
    assert errors[0]["els_status"] == "any"
    assert errors[0]["code_error"] == SCOPUS_ERRORS.get(HTTP_500)
    assert errors[1]["any"] == "any"


@mark.asyncio
async def test_starlette_http_exception():
    error = STARLETTE_HTTP_EXCEPTION
    res = await HANDLER.starlette_http_exception(REQUEST, error)
    errors = assert_error_json(res, HTTP_500, "any")
    assert errors is None


@mark.asyncio
async def test_fastapi_http_exception():
    error = FASTAPI_HTTP_EXCEPTION
    res = await HANDLER.starlette_http_exception(REQUEST, error)
    errors = assert_error_json(res, HTTP_500, "any")
    assert errors is None


@mark.asyncio
async def test_fastapi_request_validation_error():
    error = REQUEST_VALIDATION_ERROR
    res = await HANDLER.fastapi_validation_error(REQUEST, error)
    errors = assert_error_json(res, HTTP_422, "any")
    assert errors[0]["msg"] == "any"


@mark.asyncio
async def test_fastapi_response_validation_error():
    error = RESPONSE_VALIDATION_ERROR
    res = await HANDLER.fastapi_validation_error(REQUEST, error)
    errors = assert_error_json(res, HTTP_422, "any")
    assert errors[0]["msg"] == "any"


@mark.asyncio
async def test_fastapi_response_validation_filter():
    error = RESPONSE_VALIDATION_EXCEPTION_ERROR
    res = await HANDLER.fastapi_validation_error(REQUEST, error)
    errors = assert_error_json(res, HTTP_422, "any")
    assert errors[0]["msg"] == "any"
    assert errors[0]["ctx"]["error"] == "ValueError"


@mark.asyncio
async def test_pydantic_validation_error():
    error = PYDANTIC_VALIDATION_ERROR
    res = await HANDLER.pydantic_validation_error(REQUEST, error)
    errors = assert_error_json(res, HTTP_500, "Field required")
    assert errors[0]["type"] == "missing"
    assert errors[0]["msg"] == "Field required"
    assert errors[0]["input"] == "any"


@mark.asyncio
async def test_pydantic_validation_undefined():
    error = PYDANTIC_UNDEFINED_ERROR
    res = await HANDLER.pydantic_validation_error(REQUEST, error)
    errors = assert_error_json(res, HTTP_500, "Field required")
    assert errors[0]["type"] == "missing"
    assert errors[0]["msg"] == "Field required"
    assert errors[0]["input"] == "PydanticUndefined"


@mark.asyncio
async def test_rate_limit_error():
    res = await HANDLER.rate_limit_error(REQUEST, RATE_LIMIT_ERROR)
    message = f"Request rate limit of {RATE_LIMIT_ERROR.detail} exceeded"
    errors = assert_error_json(res, HTTP_429, message)
    assert errors is None
