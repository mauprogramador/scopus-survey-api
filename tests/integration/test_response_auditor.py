# mypy: disable-error-code="index"
from http import HTTPStatus

from httpx import AsyncClient as Client
from pydantic_core import ValidationError
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.domain.enums import ExcMsg
from src.core.domain.exceptions import ScopusAPIError
from src.infra.config.scopus import QUOTA_ERROR_CODE, RATE_LIMIT_ERROR_CODE
from tests.conftest import assert_error_json
from tests.mocks.errors import SCOPUS_API_QUOTA_ERROR, SCOPUS_API_RATE_ERROR
from tests.mocks.helpers import fqn, get_patch, trans
from tests.mocks.integration import (
    ONE_PAGE_ONE_ABSTRACT,
    RESPONSE_JSON_ERROR,
    RESPONSE_KEY_ERROR,
    RESPONSE_QUOTA_EXCEEDED,
    RESPONSE_RATE_LIMIT_EXCEEDED,
    RESPONSE_STATUS_ERROR,
)
from tests.mocks.raw import (
    COMBINATION_PARAMS,
    HTTP_200,
    HTTP_429,
    HTTP_500,
    HTTP_502,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_SEARCH,
)


@mark.asyncio
async def test_scopus_response(mocker: Mocker, client: Client):
    mocker.patch(*get_patch(ONE_PAGE_ONE_ABSTRACT))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200


@mark.asyncio
@mark.parametrize(
    "status",
    [
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.UNAUTHORIZED,
        HTTPStatus.FORBIDDEN,
        HTTPStatus.NOT_FOUND,
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.INTERNAL_SERVER_ERROR,
    ],
)
async def test_status_error(
    mocker: Mocker, client: Client, status: HTTPStatus
):
    RESPONSE_STATUS_ERROR.configure_mock(status=status)
    mocker.patch(*get_patch(RESPONSE_STATUS_ERROR))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    exc = ScopusAPIError(
        HTTPStatus(status),
        {"status": "any"},
        {"code": "ANY", "text": "any"},
    )
    details = assert_error_json(res, HTTP_502, trans(exc))
    assert details[0]["status"] == "ERROR"
    assert details[0]["error_code"] == "any"
    assert details[0]["status_code"] == status


@mark.asyncio
async def test_quota_exceeded(mocker: Mocker, client: Client):
    mocker.patch(*get_patch(RESPONSE_QUOTA_EXCEEDED))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    details = assert_error_json(res, HTTP_502, trans(SCOPUS_API_QUOTA_ERROR))
    assert details[0]["error_code"] == QUOTA_ERROR_CODE
    assert details[0]["status_code"] == HTTP_429


@mark.asyncio
async def test_rate_limit_exceeded(mocker: Mocker, client: Client):
    mocker.patch(*get_patch(RESPONSE_RATE_LIMIT_EXCEEDED))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    details = assert_error_json(res, HTTP_502, trans(SCOPUS_API_RATE_ERROR))
    assert details[0]["error_code"] == RATE_LIMIT_ERROR_CODE
    assert details[0]["status_code"] == HTTP_429


@mark.asyncio
async def test_json_validation_error(mocker: Mocker, client: Client):
    mocker.patch(*get_patch(RESPONSE_JSON_ERROR))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    details = assert_error_json(res, HTTP_500, ExcMsg.VALIDATE_ERROR)
    assert details[0]["type"] == fqn(ValidationError)
    assert details[0]["message"]
    assert details[0]["errors"][0]["type"] == "model_type"


@mark.asyncio
async def test_json_key_error(mocker: Mocker, client: Client):
    mocker.patch(*get_patch(RESPONSE_KEY_ERROR))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    details = assert_error_json(res, HTTP_500, ExcMsg.VALIDATE_ERROR)
    assert details[0]["type"] == fqn(ValidationError)
    assert details[0]["message"]
    assert details[0]["errors"][0]["type"] == "missing"
