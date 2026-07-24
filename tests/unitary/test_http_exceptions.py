from datetime import datetime, timezone
from json import JSONDecodeError

import aiohttp
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from itsdangerous import SignatureExpired
from pydantic import ValidationError
from pytest import mark, raises

from src.core.domain.enums import ExcMsg
from src.core.domain.exceptions import (
    BadGatewayContent,
    HTTPError,
    ScopusAPIError,
    Unauthorized,
    get_error_details,
    get_error_message,
)
from src.infra.config.scopus import RATE_LIMIT_ERROR_CODE
from tests.conftest import assert_http_error
from tests.mocks.errors import (
    CONTENT_TYPE_ERROR,
    JSON_DECODE_ERROR,
    PYDANTIC_VALIDATION_ERROR,
    REQUEST_VALIDATION_ERROR,
)
from tests.mocks.helpers import fqn, trans
from tests.mocks.raw import HTTP_401, HTTP_429, HTTP_500, HTTP_502


@mark.parametrize(
    "exc,msg",
    [
        (ValueError("any"), "any"),
        (CONTENT_TYPE_ERROR, "any"),
        (FastAPIHTTPException(HTTP_500, "any"), "any"),
        (REQUEST_VALIDATION_ERROR, repr(REQUEST_VALIDATION_ERROR)),
    ],
    ids=["args", "message", "detail", "repr"],
)
def test_get_error_message(exc: Exception, msg: str):
    assert get_error_message(exc) == msg


@mark.xfail(reason="Data leak")
def test_get_error_details():
    details = get_error_details(ValueError("any"))
    assert details["type"] == fqn(ValueError)
    assert details["message"] == "any"

    details = get_error_details(PYDANTIC_VALIDATION_ERROR)
    assert details["type"] == fqn(ValidationError)
    assert details["message"] == "Field required"
    assert details["errors"][0]["type"] == "missing"
    assert details["errors"][0]["input"] == "any"
    assert details["errors"][0]["msg"] == "Field required"
    assert "cause" not in details


def test_get_error_details_with_cause():
    try:
        data = {}
        try:
            print(data["user_id"])
        except KeyError as top_exc:
            raise RuntimeError("No User ID") from top_exc

    except Exception as exc:  # pylint: disable=W0718
        details = get_error_details(exc)

        assert details["type"] == fqn(RuntimeError)
        assert details["message"] == "No User ID"
        assert details["cause"]["type"] == fqn(KeyError)
        assert details["cause"]["message"] == "user_id"


def test_http_error():
    with raises(HTTPError) as info:
        exc = ValueError("any")
        raise HTTPError(HTTP_500, ExcMsg.INTERNAL_ERROR, exc)

    assert_http_error(info, HTTP_500, trans(info.value))
    assert info.value.details[0]["type"] == fqn(ValueError)
    assert info.value.details[0]["message"] == "any"


def test_signature_error():
    date_signed = datetime.now()
    with raises(HTTPError) as info:
        exc = SignatureExpired("any", "any", date_signed)
        raise Unauthorized(ExcMsg.INVALID_TOKEN, exc)

    assert_http_error(info, HTTP_401, trans(info.value))
    assert info.value.details[0]["type"] == fqn(SignatureExpired)
    assert info.value.details[0]["message"] == "any"

    signature = info.value.details[0]["signature"]
    assert signature["payload"] == "any"
    assert signature["date_signed"] == date_signed.replace(
        tzinfo=timezone.utc
    ).isoformat(timespec="seconds")


def test_content_type_error():
    with raises(HTTPError) as info:
        exc = CONTENT_TYPE_ERROR
        raise BadGatewayContent(ExcMsg.INVALID_JSON_ERROR, exc, "any")

    assert_http_error(info, HTTP_502, trans(info.value))
    assert info.value.details[0]["type"] == fqn(aiohttp.ContentTypeError)
    assert info.value.details[0]["message"] == "any"
    assert info.value.details[0]["body"] == "any"

    assert info.value.details[0]["error"]["message"] == "any"
    assert info.value.details[0]["error"]["status_code"] == 400
    assert info.value.details[0]["error"]["resource"] is not None


def test_content_type_error_truncate():
    with raises(HTTPError) as info:
        exc = CONTENT_TYPE_ERROR
        raise BadGatewayContent(ExcMsg.INVALID_JSON_ERROR, exc, "any" * 1000)

    assert_http_error(info, HTTP_502, trans(info.value))
    assert info.value.details[0]["type"] == fqn(aiohttp.ContentTypeError)
    assert "..." in info.value.details[0]["body"]


def test_json_decode_error():
    with raises(HTTPError) as info:
        exc = JSON_DECODE_ERROR
        raise BadGatewayContent(ExcMsg.INVALID_JSON_ERROR, exc, "any")

    assert_http_error(info, HTTP_502, trans(info.value))
    assert info.value.details[0]["type"] == fqn(JSONDecodeError)
    assert info.value.details[0]["message"] == JSON_DECODE_ERROR.args[0]
    assert info.value.details[0]["body"] == "any"

    assert info.value.details[0]["error"]["message"] == "any"
    assert info.value.details[0]["error"]["pos"] is not None
    assert info.value.details[0]["error"]["lineno"] == 1
    assert info.value.details[0]["error"]["colno"] == 1


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
        )

    assert_http_error(info, HTTP_502, "any")
    assert info.value.details[0]["limit"] == 20000
    assert info.value.details[0]["remaining"] == 0
    assert info.value.details[0]["reset"] == 1779148473
    assert info.value.details[0]["status_code"] == HTTP_429
    assert info.value.details[0]["status"] == RATE_LIMIT_ERROR_CODE
    assert info.value.details[0]["error_code"] == RATE_LIMIT_ERROR_CODE
    assert info.value.details[0]["error_text"] == "any"
    assert info.value.details[0]["docs"]
