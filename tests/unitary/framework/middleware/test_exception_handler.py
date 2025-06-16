import pytest
from fastapi.encoders import jsonable_encoder

from src.core.config.scopus import HTTP_CODE_ERRORS
from tests.conftest import assert_error_response
from tests.helpers.models import Request
from tests.mocks.fixtures import (
    FASTAPI_HTTP_EXCEPTION,
    HANDLER,
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

REQUEST = Request()


@pytest.mark.asyncio
async def test_custom_http_error():
    response = await HANDLER.custom_http_error(REQUEST, HTTP_ERROR)
    assert_error_response(response, 400, "any")


@pytest.mark.asyncio
async def test_scopus_api_error():
    response = await HANDLER.scopus_api_error(REQUEST, SCOPUS_API_ERROR)
    errors = [
        {"els_status": "any", "code_error": HTTP_CODE_ERRORS.get(500)},
        {"any": "any"},
    ]
    assert_error_response(response, 502, "Scopus API Error", errors)


@pytest.mark.asyncio
async def test_starlette_http_exception():
    error = STARLETTE_HTTP_EXCEPTION
    response = await HANDLER.starlette_http_exception(REQUEST, error)
    assert_error_response(response, 500, "any")


@pytest.mark.asyncio
async def test_fastapi_http_exception():
    error = FASTAPI_HTTP_EXCEPTION
    response = await HANDLER.starlette_http_exception(REQUEST, error)
    assert_error_response(response, 500, "any")


@pytest.mark.asyncio
async def test_fastapi_request_validation_error():
    error = REQUEST_VALIDATION_ERROR
    response = await HANDLER.fastapi_validation_error(REQUEST, error)
    assert_error_response(response, 422, "any", [{"msg": "any"}])


@pytest.mark.asyncio
async def test_fastapi_response_validation_error():
    error = RESPONSE_VALIDATION_ERROR
    response = await HANDLER.fastapi_validation_error(REQUEST, error)
    assert_error_response(response, 422, "any", [{"msg": "any"}])


@pytest.mark.asyncio
async def test_fastapi_response_validation_filter():
    error = RESPONSE_VALIDATION_EXCEPTION_ERROR
    response = await HANDLER.fastapi_validation_error(REQUEST, error)
    errors = error.errors()
    errors[0]["ctx"]["error"] = type(ValueError("any")).__name__
    errors = jsonable_encoder(errors)
    assert_error_response(response, 422, "any", errors)


@pytest.mark.asyncio
async def test_pydantic_validation_error():
    error = PYDANTIC_VALIDATION_ERROR
    response = await HANDLER.pydantic_validation_error(REQUEST, error)
    errors = jsonable_encoder(error.errors(include_url=False))
    assert_error_response(response, 500, "Field required", errors)


@pytest.mark.asyncio
async def test_pydantic_validation_undefined():
    error = PYDANTIC_UNDEFINED_ERROR
    response = await HANDLER.pydantic_validation_error(REQUEST, error)
    errors = error.errors(include_url=False)
    errors[0]["input"] = "PydanticUndefined"
    errors = jsonable_encoder(errors)
    assert_error_response(response, 500, "Field required", errors)


@pytest.mark.asyncio
async def test_rate_limit_error():
    response = await HANDLER.rate_limit_error(REQUEST, RATE_LIMIT_ERROR)
    message = f"Request rate limit of {RATE_LIMIT_ERROR.detail} exceeded"
    assert_error_response(response, 429, message)
