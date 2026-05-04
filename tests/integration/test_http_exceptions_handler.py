# mypy: disable-error-code="index"
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.adapters.presenters.csv_response import CSVResponse
from src.core.config.scopus import SCOPUS_ERRORS
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
    CSV_PARAMS,
    HTTP_400,
    HTTP_422,
    HTTP_429,
    HTTP_500,
    HTTP_502,
    URL_CSV,
)


RETRIEVE = fqn(CSVResponse.retrieve)


@mark.asyncio
async def test_custom_http_error(mocker: Mocker, client: Client):
    mocker.patch(RETRIEVE, side_effect=HTTP_ERROR)
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_400, "any")
    assert errors[0]["type"] == fqn(ValueError)
    assert errors[0]["detail"] == "any"


@mark.asyncio
async def test_scopus_api_error(mocker: Mocker, client: Client):
    mocker.patch(RETRIEVE, side_effect=SCOPUS_API_ERROR)
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_502, "Scopus API Error")
    assert errors[0]["els_status"] == "any"
    assert errors[0]["code_error"] == SCOPUS_ERRORS.get(HTTP_500)
    assert errors[1]["any"] == "any"


@mark.asyncio
async def test_starlette_http_exception(mocker: Mocker, client: Client):
    mocker.patch(RETRIEVE, side_effect=STARLETTE_HTTP_EXCEPTION)
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_500, "any")
    assert errors is None


@mark.asyncio
async def test_fastapi_http_exception(mocker: Mocker, client: Client):
    mocker.patch(RETRIEVE, side_effect=FASTAPI_HTTP_EXCEPTION)
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_500, "any")
    assert errors is None


@mark.asyncio
async def test_fastapi_request_validation_error(
    mocker: Mocker, client: Client
):
    mocker.patch(RETRIEVE, side_effect=REQUEST_VALIDATION_ERROR)
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_422, "any")
    assert errors[0]["msg"] == "any"


@mark.asyncio
async def test_fastapi_response_validation_error(
    mocker: Mocker, client: Client
):
    mocker.patch(RETRIEVE, side_effect=RESPONSE_VALIDATION_ERROR)
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_422, "any")
    assert errors[0]["msg"] == "any"


@mark.asyncio
async def test_fastapi_response_validation_error_filter(
    mocker: Mocker, client: Client
):
    mocker.patch(RETRIEVE, side_effect=RESPONSE_VALIDATION_EXCEPTION_ERROR)
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_422, "any")
    assert errors[0]["msg"] == "any"
    assert errors[0]["ctx"]["error"] == "ValueError"


@mark.asyncio
async def test_pydantic_validation_error(mocker: Mocker, client: Client):
    mocker.patch(RETRIEVE, side_effect=PYDANTIC_VALIDATION_ERROR)
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_500, "Field required")
    assert errors[0]["type"] == "missing"
    assert errors[0]["msg"] == "Field required"
    assert errors[0]["input"] == "any"


@mark.asyncio
async def test_pydantic_validation_undefined(mocker: Mocker, client: Client):
    mocker.patch(RETRIEVE, side_effect=PYDANTIC_UNDEFINED_ERROR)
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_500, "Field required")
    assert errors[0]["type"] == "missing"
    assert errors[0]["msg"] == "Field required"
    assert errors[0]["input"] == "PydanticUndefined"


@mark.asyncio
async def test_rate_limit_error(mocker: Mocker, client: Client):
    mocker.patch(RETRIEVE, side_effect=RATE_LIMIT_ERROR)
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    message = f"Request rate limit of {RATE_LIMIT_ERROR.detail} exceeded"
    errors = assert_error_json(res, HTTP_429, message)
    assert errors is None
