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
    COMMON_ERROR_EXC_GROUP,
    FASTAPI_HTTP_EXCEPTION,
    HTTP_ERROR,
    HTTP_ERROR_EXC_GROUP,
    PYDANTIC_ERROR_EXC_GROUP,
    PYDANTIC_VALIDATION_ERROR,
    RATE_LIMIT_ERROR,
    REQUEST_VALIDATION_ERROR,
    RESPONSE_VALIDATION_ERROR,
    SCOPUS_API_ERROR,
    SCOPUS_API_ERROR_EXC_GROUP,
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


def test_common_error():
    res = handler.common_error(REQUEST, KeyError("any"))
    details = assert_error_json(res, HTTP_500, ExcMsg.INTERNAL_ERROR)
    assert details[0]["type"] == fqn(KeyError)
    assert details[0]["message"] == "any"


@mark.parametrize(
    "exc_group,details_count",
    [
        (COMMON_ERROR_EXC_GROUP, 3),
        (HTTP_ERROR_EXC_GROUP, 3),
        (PYDANTIC_ERROR_EXC_GROUP, 3),
        (SCOPUS_API_ERROR_EXC_GROUP, 3),
    ],
    ids=["Common", "HTTP", "Pydantic", "Scopus API"],
)
def test_common_error_exc_group(exc_group: ExceptionGroup, details_count: int):
    res = handler.common_error(REQUEST, exc_group)
    details = assert_error_json(res, HTTP_500, ExcMsg.INTERNAL_ERROR)
    assert details[0]["type"] == fqn(ExceptionGroup)
    assert details[0]["message"] == "any"
    assert len(details) == details_count

    if "type" in details[1]:
        assert details[1]["type"] == fqn(type(exc_group.exceptions[0]))
    else:
        assert details[1]["error_code"] == "ANY"


@mark.asyncio
async def test_custom_http_error():
    res = await handler.custom_http_error(REQUEST, HTTP_ERROR)
    details = assert_error_json(res, HTTP_400, ExcMsg.INTERNAL_ERROR)
    assert details[0]["type"] == fqn(ValueError)
    assert details[0]["message"] == "any"


@mark.asyncio
async def test_scopus_api_error():
    res = await handler.scopus_api_error(REQUEST, SCOPUS_API_ERROR)
    details = assert_error_json(res, HTTP_502, trans(SCOPUS_API_ERROR))
    assert details[0]["status_code"] == HTTP_500
    assert details[0]["error_code"] == "ANY"


@mark.asyncio
async def test_starlette_http_exception():
    exc = STARLETTE_HTTP_EXCEPTION
    res = await handler.starlette_http_exception(REQUEST, exc)
    details = assert_error_json(res, HTTP_500, trans(exc))
    assert details[0]["type"] == fqn(StarletteHTTPException)
    assert details[0]["message"] == "any"


@mark.asyncio
async def test_fastapi_http_exception():
    exc = FASTAPI_HTTP_EXCEPTION
    res = await handler.starlette_http_exception(REQUEST, exc)
    details = assert_error_json(res, HTTP_500, trans(exc))
    assert details[0]["type"] == fqn(FastAPIHTTPException)
    assert details[0]["message"] == "any"


@mark.asyncio
async def test_fastapi_request_validation_error():
    exc = REQUEST_VALIDATION_ERROR
    res = await handler.fastapi_validation_error(REQUEST, exc)
    details = assert_error_json(res, HTTP_422, trans(exc))
    assert details[0]["type"] == fqn(RequestValidationError)
    assert details[0]["message"] == "any"
    assert details[0]["errors"][0]["msg"] == "any"


@mark.asyncio
async def test_fastapi_response_validation_error():
    exc = RESPONSE_VALIDATION_ERROR
    res = await handler.fastapi_validation_error(REQUEST, exc)
    details = assert_error_json(res, HTTP_500, trans(exc))
    assert details[0]["type"] == fqn(ResponseValidationError)
    assert details[0]["message"] == "any"
    assert details[0]["errors"][0]["msg"] == "any"


@mark.asyncio
async def test_pydantic_validation_error():
    exc = PYDANTIC_VALIDATION_ERROR
    res = await handler.pydantic_validation_error(REQUEST, exc)
    details = assert_error_json(res, HTTP_500, trans(exc))
    assert details[0]["type"] == fqn(ValidationError)
    assert details[0]["message"] == "Field required"
    assert details[0]["errors"][0]["type"] == "missing"
    assert details[0]["errors"][0]["msg"] == "Field required"
    assert details[0]["errors"][0]["input"] == "any"


@mark.asyncio
async def test_rate_limit_error():
    res = await handler.rate_limit_error(REQUEST, RATE_LIMIT_ERROR)
    details = assert_error_json(res, HTTP_429, trans(RATE_LIMIT_ERROR))
    assert details[0]["type"] == fqn(RateLimitExceeded)
    assert details[0]["message"] == ExcMsg.SLOWAPI_RATE_ERROR
    assert details[0]["error"]["status_code"] == HTTP_429
    assert details[0]["error"]["resource"] is not None
    assert details[0]["error"]["rate"] == RATE_LIMIT_ERROR.detail
