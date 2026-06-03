# mypy: disable-error-code="index"
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from httpx import AsyncClient as Client
from pydantic import ValidationError
from pytest import mark
from pytest_mock import MockerFixture as Mocker
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.adapters.presenters.csv_response import CSVResponse
from src.core.data.enums import ExcMsg
from src.framework.fastapi.routes import favicon
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
from tests.mocks.helpers import Patch, fqn, trans
from tests.mocks.raw import (
    CSV_PARAMS,
    HTTP_400,
    HTTP_422,
    HTTP_429,
    HTTP_500,
    HTTP_502,
    URL_CSV,
)


RETRIEVE = Patch(CSVResponse.retrieve).classmethod(favicon)


@mark.asyncio
async def test_custom_http_error(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(HTTP_ERROR))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_400, ExcMsg.UNEXPECTED_ERROR)
    assert errors[0]["type"] == fqn(ValueError)
    assert errors[0]["message"] == "any"


@mark.asyncio
async def test_scopus_api_error(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(SCOPUS_API_ERROR))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_502, trans(SCOPUS_API_ERROR))
    assert errors[0]["status_code"] == HTTP_500.value
    assert errors[0]["error_code"] == "ANY"
    assert errors[1]["any"] == "any"


@mark.asyncio
async def test_starlette_http_exception(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(STARLETTE_HTTP_EXCEPTION))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_500, trans(STARLETTE_HTTP_EXCEPTION))
    assert errors[0]["type"] == fqn(StarletteHTTPException)
    assert errors[0]["message"] == "any"


@mark.asyncio
async def test_fastapi_http_exception(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(FASTAPI_HTTP_EXCEPTION))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_500, trans(FASTAPI_HTTP_EXCEPTION))
    assert errors[0]["type"] == fqn(FastAPIHTTPException)
    assert errors[0]["message"] == "any"


@mark.asyncio
async def test_fastapi_request_validation_error(
    mocker: Mocker, client: Client
):
    mocker.patch(**RETRIEVE(REQUEST_VALIDATION_ERROR))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_422, trans(REQUEST_VALIDATION_ERROR))
    assert errors[0]["type"] == fqn(RequestValidationError)
    assert errors[0]["message"] == "any"
    assert errors[1]["msg"] == "any"


@mark.asyncio
async def test_fastapi_response_validation_error(
    mocker: Mocker, client: Client
):
    mocker.patch(**RETRIEVE(RESPONSE_VALIDATION_ERROR))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_500, trans(RESPONSE_VALIDATION_ERROR))
    assert errors[0]["type"] == fqn(ResponseValidationError)
    assert errors[0]["message"] == "any"
    assert errors[1]["msg"] == "any"


@mark.asyncio
async def test_pydantic_validation_error(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(PYDANTIC_VALIDATION_ERROR))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_500, trans(PYDANTIC_VALIDATION_ERROR))
    assert errors[0]["type"] == fqn(ValidationError)
    assert errors[0]["message"] == "Field required"
    assert errors[1]["type"] == "missing"
    assert errors[1]["msg"] == "Field required"
    assert errors[1]["input"] == "any"


@mark.asyncio
async def test_rate_limit_error(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(RATE_LIMIT_ERROR))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_429, trans(RATE_LIMIT_ERROR))
    assert errors[0]["type"] == fqn(RateLimitExceeded)
    assert errors[0]["message"] == "any"
    assert errors[1]["status_code"] == 429 and errors[1]["limit"] is not None
    assert errors[1]["rate"] == RATE_LIMIT_ERROR.detail
