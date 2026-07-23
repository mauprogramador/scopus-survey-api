# mypy: disable-error-code="index"
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from httpx import AsyncClient as Client
from pydantic import ValidationError
from pytest import mark
from pytest_mock import MockerFixture as Mocker
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.adapters.presenters.csv_response import retrieve_csv
from src.core.data.enums import ExcMsg
from src.framework.fastapi.routes import favicon
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


RETRIEVE = Patch(favicon, retrieve_csv)


@mark.asyncio
async def test_common_error(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(KeyError("any")))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_500, ExcMsg.INTERNAL_ERROR)
    assert details[0]["type"] == fqn(KeyError)
    assert details[0]["message"] == "any"


@mark.asyncio
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
async def test_common_error_exc_group(
    mocker: Mocker,
    client: Client,
    exc_group: ExceptionGroup,
    details_count: int,
):
    mocker.patch(**RETRIEVE(exc_group))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_500, ExcMsg.INTERNAL_ERROR)
    assert details[0]["type"] == fqn(ExceptionGroup)
    assert details[0]["message"] == "any"
    assert len(details) == details_count

    if "type" in details[1]:
        assert details[1]["type"] == fqn(type(exc_group.exceptions[0]))
    else:
        assert details[1]["error_code"] == "ANY"


@mark.asyncio
async def test_custom_http_error(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(HTTP_ERROR))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_400, ExcMsg.INTERNAL_ERROR)
    assert details[0]["type"] == fqn(ValueError)
    assert details[0]["message"] == "any"


@mark.asyncio
async def test_scopus_api_error(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(SCOPUS_API_ERROR))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_502, trans(SCOPUS_API_ERROR))
    assert details[0]["status_code"] == HTTP_500.value
    assert details[0]["error_code"] == "ANY"


@mark.asyncio
async def test_starlette_http_exception(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(STARLETTE_HTTP_EXCEPTION))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_500, trans(STARLETTE_HTTP_EXCEPTION))
    assert details[0]["type"] == fqn(StarletteHTTPException)
    assert details[0]["message"] == "any"


@mark.asyncio
async def test_fastapi_http_exception(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(FASTAPI_HTTP_EXCEPTION))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_500, trans(FASTAPI_HTTP_EXCEPTION))
    assert details[0]["type"] == fqn(FastAPIHTTPException)
    assert details[0]["message"] == "any"


@mark.asyncio
async def test_fastapi_request_validation_error(
    mocker: Mocker, client: Client
):
    mocker.patch(**RETRIEVE(REQUEST_VALIDATION_ERROR))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_422, trans(REQUEST_VALIDATION_ERROR))
    assert details[0]["type"] == fqn(RequestValidationError)
    assert details[0]["message"] == "any"
    assert details[0]["errors"][0]["msg"] == "any"


@mark.asyncio
async def test_fastapi_response_validation_error(
    mocker: Mocker, client: Client
):
    mocker.patch(**RETRIEVE(RESPONSE_VALIDATION_ERROR))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(
        res, HTTP_500, trans(RESPONSE_VALIDATION_ERROR)
    )
    assert details[0]["type"] == fqn(ResponseValidationError)
    assert details[0]["message"] == "any"
    assert details[0]["errors"][0]["msg"] == "any"


@mark.asyncio
async def test_pydantic_validation_error(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(PYDANTIC_VALIDATION_ERROR))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    msg = trans(PYDANTIC_VALIDATION_ERROR)
    details = assert_error_json(res, HTTP_500, msg)
    assert details[0]["type"] == fqn(ValidationError)
    assert details[0]["message"] == "Field required"
    assert details[0]["errors"][0]["type"] == "missing"
    assert details[0]["errors"][0]["msg"] == "Field required"
    assert details[0]["errors"][0]["input"] == "any"


@mark.asyncio
async def test_rate_limit_error(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(RATE_LIMIT_ERROR))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_429, trans(RATE_LIMIT_ERROR))
    assert details[0]["type"] == fqn(RateLimitExceeded)
    assert details[0]["message"] == ExcMsg.SLOWAPI_RATE_ERROR
    assert details[0]["error"]["status_code"] == HTTP_429
    assert URL_CSV in details[0]["error"]["resource"]
    assert details[0]["error"]["rate"] == RATE_LIMIT_ERROR.detail
