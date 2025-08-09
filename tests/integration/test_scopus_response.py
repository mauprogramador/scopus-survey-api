# mypy: disable-error-code="index"
from http import HTTPStatus
from unittest.mock import AsyncMock

from aiohttp_retry import RetryClient
from httpx import AsyncClient as Client
from pydantic_core import ValidationError
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.common.error_messages import SCOPUS_API_ERROR, VALIDATE_ERROR
from src.core.config.scopus import SCOPUS_ERRORS
from src.core.data.enums import ScopusCode
from tests.conftest import assert_error_json
from tests.mocks.helpers import fqn
from tests.mocks.integration import (
    RESPONSE_JSON_ERROR,
    RESPONSE_KEY_ERROR,
    RESPONSE_QUOTA_EXCEEDED,
    RESPONSE_RATE_LIMIT_EXCEEDED,
    RESPONSE_STATUS_ERROR,
    SEARCH_ONE_PAGE_ONE_RESULT,
)
from tests.mocks.raw import (
    COMBINATION_PARAMS,
    HTTP_200,
    HTTP_429,
    HTTP_500,
    HTTP_502,
    RAW_SERVICE_ERROR_QUOTA,
    RAW_ERROR_RESPONSE_RATE_LIMIT,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_SEARCH,
)

GET = fqn(RetryClient.get)


@mark.asyncio
async def test_scopus_response(mocker: Mocker, client: Client):
    mocker.patch(
        GET,
        new=AsyncMock(side_effect=SEARCH_ONE_PAGE_ONE_RESULT),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200


@mark.asyncio
@mark.parametrize("status", SCOPUS_ERRORS.keys())
async def test_status_error(
    mocker: Mocker, client: Client, status: HTTPStatus
):
    RESPONSE_STATUS_ERROR.status = status
    mocker.patch(GET, new=AsyncMock(return_value=RESPONSE_STATUS_ERROR))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    errors = assert_error_json(res, HTTP_502, SCOPUS_API_ERROR)
    assert errors[0]["els_status"] and errors[1]["error"] == "any"
    assert errors[0]["code_error"] == SCOPUS_ERRORS.get(status)


@mark.asyncio
async def test_quota_exceeded(mocker: Mocker, client: Client):
    mocker.patch(GET, new=AsyncMock(return_value=RESPONSE_QUOTA_EXCEEDED))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    errors = assert_error_json(res, HTTP_502, SCOPUS_API_ERROR)
    assert errors[0]["els_status"] == ScopusCode.QUOTA
    assert errors[0]["code_error"] == SCOPUS_ERRORS.get(HTTP_429)
    assert errors[1] == RAW_SERVICE_ERROR_QUOTA


@mark.asyncio
async def test_rate_limit_exceeded(mocker: Mocker, client: Client):
    mocker.patch(GET, new=AsyncMock(return_value=RESPONSE_RATE_LIMIT_EXCEEDED))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    errors = assert_error_json(res, HTTP_502, SCOPUS_API_ERROR)
    assert errors[0]["els_status"] == ScopusCode.RATE_LIMIT
    assert errors[0]["code_error"] == SCOPUS_ERRORS.get(HTTP_429)
    assert errors[1] == RAW_ERROR_RESPONSE_RATE_LIMIT


@mark.asyncio
async def test_json_validation_error(mocker: Mocker, client: Client):
    mocker.patch(GET, new=AsyncMock(return_value=RESPONSE_JSON_ERROR))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    errors = assert_error_json(res, HTTP_500, VALIDATE_ERROR)
    assert errors[0]["type"] == fqn(ValidationError)
    assert errors[0]["file"] and errors[0]["line"]
    assert errors[0]["detail"]
    assert errors[1]["type"] == "model_type"


@mark.asyncio
async def test_json_key_error(mocker: Mocker, client: Client):
    mocker.patch(GET, new=AsyncMock(return_value=RESPONSE_KEY_ERROR))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    errors = assert_error_json(res, HTTP_500, VALIDATE_ERROR)
    assert errors[0]["type"] == fqn(KeyError)
    assert errors[0]["file"] and errors[0]["line"]
    assert errors[0]["detail"]
