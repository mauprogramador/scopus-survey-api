from http import HTTPStatus

from fastapi import HTTPException
from itsdangerous import BadData
from pydantic import ValidationError
from pytest import raises
from requests import RequestException

from src.core.common.types import Token
from src.core.config.scopus import HTTP_CODE_ERRORS
from src.core.data.enums import ScopusCode
from src.core.domain.http_exceptions import HTTPError, ScopusAPIError
from tests.conftest import assert_http_error


def test_http_error_exception():
    error_class = "builtins.ValueError"
    with raises(HTTPError) as exc:
        try:
            raise ValueError("any")
        except ValueError as exc:
            raise HTTPError(
                HTTPStatus.INTERNAL_SERVER_ERROR, "any", exc
            ) from exc

    assert_http_error(exc, 500, "any")
    assert exc.value.errors[0]["type"] == error_class
    assert exc.value.errors[0]["file"] and exc.value.errors[0]["line"]
    assert exc.value.errors[0]["detail"] == "any"


def test_http_error_http_exception():
    error_class = "fastapi.exceptions.HTTPException"
    with raises(HTTPError) as exc:
        try:
            raise HTTPException(500, "any")
        except HTTPException as exc:
            raise HTTPError(
                HTTPStatus.INTERNAL_SERVER_ERROR, "any", exc
            ) from exc

    assert_http_error(exc, 500, "any")
    assert exc.value.errors[0]["type"] == error_class
    assert exc.value.errors[0]["file"] and exc.value.errors[0]["line"]
    assert exc.value.errors[0]["detail"] == "any"
    assert exc.value.errors[0]["status_code"] == 500


def test_http_error_validation_error():
    error_class = "pydantic_core._pydantic_core.ValidationError"
    with raises(HTTPError) as exc:
        try:
            Token.validate_python("any")
        except ValidationError as exc:
            raise HTTPError(
                HTTPStatus.INTERNAL_SERVER_ERROR, "any", exc
            ) from exc

    assert_http_error(exc, 500, "any")
    assert exc.value.errors[0]["type"] == error_class
    assert exc.value.errors[0]["file"] and exc.value.errors[0]["line"]
    assert exc.value.errors[1]["type"] == "string_too_short"


def test_http_error_request_exception():
    error_class = "requests.exceptions.RequestException"
    with raises(HTTPError) as exc:
        try:
            raise RequestException("any")
        except RequestException as exc:
            raise HTTPError(
                HTTPStatus.INTERNAL_SERVER_ERROR, "any", exc
            ) from exc

    assert_http_error(exc, 500, "any")
    assert exc.value.errors[0]["type"] == error_class
    assert exc.value.errors[0]["file"] and exc.value.errors[0]["line"]
    assert exc.value.errors[0]["request_exception"]


def test_http_error_bad_data():
    error_class = "itsdangerous.exc.BadData"
    with raises(HTTPError) as exc:
        try:
            raise BadData("any")
        except BadData as exc:
            raise HTTPError(
                HTTPStatus.INTERNAL_SERVER_ERROR, "any", exc
            ) from exc

    assert_http_error(exc, 500, "any")
    assert exc.value.errors[0]["type"] == error_class
    assert exc.value.errors[0]["file"] and exc.value.errors[0]["line"]
    assert exc.value.errors[0]["bad_data"] == "any"


def test_scopus_api_error():
    json = {"error-response": {"error-code": ScopusCode.RATE_LIMIT}}
    with raises(ScopusAPIError) as exc:
        raise ScopusAPIError(500, json, ScopusCode.RATE_LIMIT)

    assert_http_error(exc, 502, "Scopus API Error")
    assert exc.value.errors[0]["els_status"] == ScopusCode.RATE_LIMIT
    assert exc.value.errors[0]["code_error"] == HTTP_CODE_ERRORS.get(500)
    assert exc.value.errors[1] == json
