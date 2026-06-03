from asyncio import TimeoutError as AsyncTimeoutError
from datetime import datetime
from json import JSONDecodeError

from aiohttp import ContentTypeError
from fastapi import HTTPException
from itsdangerous import SignatureExpired
from pydantic import ValidationError
from pytest import mark, raises

from src.core.config.scopus import RATE_LIMIT_ERROR_CODE
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import (
    BadGatewayContent,
    GatewayTimeout,
    HTTPError,
    ScopusAPIError,
    Unauthorized,
    get_error_details,
    get_error_message,
)
from tests.conftest import assert_http_error
from tests.mocks.errors import (
    CONTENT_TYPE_ERROR,
    JSON_DECODE_ERROR,
    PYDANTIC_VALIDATION_ERROR,
    REQUEST_VALIDATION_ERROR,
)
from tests.mocks.helpers import fqn, trans
from tests.mocks.raw import (
    HTTP_401,
    HTTP_429,
    HTTP_500,
    HTTP_502,
    HTTP_504,
    RAW_ERROR_RESPONSE_RATE_LIMIT,
)


@mark.parametrize(
    "exc,msg",
    [
        (ValueError("any"), "any"),
        (CONTENT_TYPE_ERROR, "any"),
        (HTTPException(HTTP_500, "any"), "any"),
        (REQUEST_VALIDATION_ERROR, repr(REQUEST_VALIDATION_ERROR)),
    ],
    ids=["args", "message", "detail", "repr"],
)
def test_get_error_message(exc: Exception, msg: str):
    assert get_error_message(exc) == msg


def test_get_error_details():
    errors = get_error_details(ValueError("any"))
    assert errors[0]["type"] == fqn(ValueError) and len(errors) == 1
    assert errors[0]["file"] and errors[0]["line"]
    assert errors[0]["message"] == "any"

    errors = get_error_details(PYDANTIC_VALIDATION_ERROR)
    assert errors[0]["type"] == fqn(ValidationError) and len(errors) == 2
    assert errors[0]["file"] and errors[0]["line"]
    assert errors[0]["message"] == "Field required"
    assert errors[1]["type"] == "missing" and errors[1]["input"] == "any"
    assert errors[1]["msg"] == "Field required" and "loc" in errors[1]


def test_http_error():
    with raises(HTTPError) as info:
        exc = ValueError("any")
        raise HTTPError(HTTP_500, ExcMsg.UNEXPECTED_ERROR, exc)

    assert_http_error(info, HTTP_500, trans(info.value))
    assert info.value.errors[0]["type"] == fqn(ValueError)
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]
    assert info.value.errors[0]["message"] == "any"


def test_signature_error():
    date_signed = datetime.now()
    with raises(HTTPError) as info:
        exc = SignatureExpired("any", "any", date_signed)
        raise Unauthorized(ExcMsg.INVALID_TOKEN, exc)

    assert_http_error(info, HTTP_401, trans(info.value))
    assert info.value.errors[0]["type"] == fqn(SignatureExpired)
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]
    assert info.value.errors[0]["message"] == "any"
    assert info.value.errors[1]["payload"] == "any"
    assert info.value.errors[1]["date_signed"] == date_signed


def test_async_timeout_error():
    with raises(HTTPError) as info:
        exc = AsyncTimeoutError("any")
        raise GatewayTimeout(ExcMsg.CONNECTION_TIMEOUT, exc)

    assert_http_error(info, HTTP_504, trans(info.value))
    assert info.value.errors[0]["type"] == fqn(AsyncTimeoutError)
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]
    assert info.value.errors[0]["message"] == "any"
    assert not info.value.errors[1]["strerror"]
    assert not info.value.errors[1]["errno"]


def test_content_type_error():
    with raises(HTTPError) as info:
        exc = CONTENT_TYPE_ERROR
        raise BadGatewayContent(ExcMsg.INVALID_JSON_ERROR, exc, "any")

    assert_http_error(info, HTTP_502, trans(info.value))
    assert info.value.errors[0]["type"] == fqn(ContentTypeError)
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]
    assert info.value.errors[0]["message"] == "any"

    assert info.value.errors[1]["raw_body"] == "any"
    assert info.value.errors[1]["message"] == "any"
    assert info.value.errors[1]["status_code"] == 400
    assert info.value.errors[1]["url"] is not None
    assert info.value.errors[1]["headers"] is None


def test_json_decode_error():
    with raises(HTTPError) as info:
        exc = JSON_DECODE_ERROR
        raise BadGatewayContent(ExcMsg.INVALID_JSON_ERROR, exc, "any")

    assert_http_error(info, HTTP_502, trans(info.value))
    assert info.value.errors[0]["type"] == fqn(JSONDecodeError)
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]
    assert info.value.errors[0]["message"] == JSON_DECODE_ERROR.args[0]

    assert info.value.errors[1]["raw_body"] == "any"
    assert info.value.errors[1]["message"] == "any"
    assert info.value.errors[1]["doc"] == "any"
    assert info.value.errors[1]["pos"] is not None
    assert info.value.errors[1]["lineno"] == 1
    assert info.value.errors[1]["colno"] == 1


def test_scopus_api_error():
    with raises(ScopusAPIError) as info:
        raise ScopusAPIError(
            HTTP_429,
            {
                "limit": 20000,
                "remaining": 0,
                "reset": 1779148473,
                "status": RATE_LIMIT_ERROR_CODE,
            },
            {"code": RATE_LIMIT_ERROR_CODE, "text": "any"},
            RAW_ERROR_RESPONSE_RATE_LIMIT,
        )

    assert_http_error(info, HTTP_502, "any")
    assert len(info.value.errors) == 2
    assert info.value.errors[0]["limit"] == 20000
    assert info.value.errors[0]["remaining"] == 0
    assert info.value.errors[0]["reset"] == 1779148473
    assert info.value.errors[0]["status_code"] == HTTP_429
    assert info.value.errors[0]["status"] == HTTP_429.phrase
    assert info.value.errors[0]["error_code"] == RATE_LIMIT_ERROR_CODE
    assert info.value.errors[0]["error_text"] == "any"
    assert info.value.errors[0]["docs"]
    assert info.value.errors[1] == RAW_ERROR_RESPONSE_RATE_LIMIT
