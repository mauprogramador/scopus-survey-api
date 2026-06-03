from asyncio import CancelledError
from asyncio import TimeoutError as AsyncTimeoutError

from aiohttp import ClientError, ClientResponseError, RequestInfo
from fastapi import HTTPException
from itsdangerous import BadData
from pydantic import ValidationError
from pytest import raises

from src.core.common.types import Token
from src.core.config.scopus import SCOPUS_ERRORS, RATE_LIMIT_ERROR_CODE
from src.core.domain.http_exceptions import HTTPError, ScopusAPIError
from tests.conftest import assert_http_error
from tests.mocks.helpers import fqn
from tests.mocks.raw import (
    HTTP_400,
    HTTP_500,
    HTTP_502,
    RAW_ERROR_RESPONSE_RATE_LIMIT,
)


def test_common_exception():
    with raises(HTTPError) as info:
        try:
            raise ValueError("any")
        except ValueError as exc:
            raise HTTPError(HTTP_500, "any", exc) from exc

    assert_http_error(info, HTTP_500, "any")
    assert info.value.errors[0]["type"] == fqn(ValueError)
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]
    assert info.value.errors[0]["detail"] == "any"


def test_http_exception():
    with raises(HTTPError) as info:
        try:
            raise HTTPException(HTTP_500, "any")
        except HTTPException as exc:
            raise HTTPError(HTTP_500, "any", exc) from exc

    assert_http_error(info, HTTP_500, "any")
    assert info.value.errors[0]["type"] == fqn(HTTPException)
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]
    assert info.value.errors[0]["detail"] == "any"
    assert info.value.errors[0]["status_code"] == HTTP_500


def test_validation_error():
    with raises(HTTPError) as info:
        try:
            Token.validate_python("any")
        except ValidationError as exc:
            raise HTTPError(HTTP_500, "any", exc) from exc

    assert_http_error(info, HTTP_500, "any")
    assert info.value.errors[0]["type"] == fqn(ValidationError)
    assert info.value.errors[0]["detail"]
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]
    assert info.value.errors[1]["type"] == "string_too_short"


def test_async_cancelled_error():
    with raises(HTTPError) as info:
        try:
            raise CancelledError("any")
        except CancelledError as exc:
            raise HTTPError(HTTP_500, "any", exc) from exc

    assert_http_error(info, HTTP_500, "any")
    assert info.value.errors[0]["type"] == fqn(CancelledError)
    assert info.value.errors[0]["detail"] == "any"
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]


def test_async_timeout_error():
    with raises(HTTPError) as info:
        try:
            raise AsyncTimeoutError("any")
        except AsyncTimeoutError as exc:
            raise HTTPError(HTTP_500, "any", exc) from exc

    assert_http_error(info, HTTP_500, "any")
    assert info.value.errors[0]["type"] == fqn(AsyncTimeoutError)
    assert info.value.errors[0]["detail"] == "any"
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]
    assert not info.value.errors[0]["strerror"]
    assert not info.value.errors[0]["errno"]


def test_client_error():
    with raises(HTTPError) as info:
        try:
            raise ClientError("any")
        except ClientError as exc:
            raise HTTPError(HTTP_500, "any", exc) from exc

    assert_http_error(info, HTTP_500, "any")
    assert info.value.errors[0]["type"] == fqn(ClientError)
    assert info.value.errors[0]["detail"] == "any"
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]


def test_bad_data():
    with raises(HTTPError) as info:
        try:
            raise BadData("any")
        except BadData as exc:
            raise HTTPError(HTTP_500, "any", exc) from exc

    assert_http_error(info, HTTP_500, "any")
    assert info.value.errors[0]["type"] == fqn(BadData)
    assert info.value.errors[0]["detail"] == "any"
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]


def test_client_response_error():
    with raises(HTTPError) as info:
        try:
            raise ClientResponseError(
                RequestInfo("any", "GET", {"Accept": "application/json"}),
                (),
                status=HTTP_400,
                message="any",
            )
        except ClientResponseError as exc:
            raise HTTPError(HTTP_500, "any", exc) from exc

    assert_http_error(info, HTTP_500, "any")
    assert info.value.errors[0]["type"] == fqn(ClientResponseError)
    assert info.value.errors[0]["detail"] == "any"
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]


def test_scopus_api_error():
    with raises(ScopusAPIError) as info:
        raise ScopusAPIError(
            HTTP_500,
            RAW_ERROR_RESPONSE_RATE_LIMIT,
            {
                "limit": 20000,
                "remaining": 0,
                "reset": 1779148473,
                "status": RATE_LIMIT_ERROR_CODE,
                "reset_datetime": "2026-05-18 19:54:33",
                "els_status": RATE_LIMIT_ERROR_CODE,
            },
            {"code": RATE_LIMIT_ERROR_CODE, "text": "any"},
        )

    assert_http_error(info, HTTP_502, ScopusCode.RATE_LIMIT)
    assert len(info.value.errors) == 2
    assert info.value.errors[0]["limit"] == 20000
    assert info.value.errors[0]["remaining"] == 0
    assert info.value.errors[0]["reset"] == 1779148473
    assert info.value.errors[0]["status"] == RATE_LIMIT_ERROR_CODE
    assert info.value.errors[0]["reset_datetime"] == "2026-05-18 19:54:33"
    assert info.value.errors[0]["els_status"] == RATE_LIMIT_ERROR_CODE
    assert info.value.errors[0]["code_error"] == SCOPUS_ERRORS.get(HTTP_500)
    assert info.value.errors[1] == RAW_ERROR_RESPONSE_RATE_LIMIT
