from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic_core import ValidationError
from pytest import raises
from pytest_mock import MockerFixture as Mocker

from src.core.common.error_messages import (
    EXPIRED_TOKEN,
    INVALID_TOKEN,
    TOKEN_COOKIE_ERROR,
    TOKEN_HEADER_ERROR,
    TOKEN_SIGNATURE_ERROR,
)
from src.core.config.config import MAX_AGE
from src.core.domain.http_exceptions import Unauthorized
from src.framework.fastapi.csrf_token import CSRFToken
from tests.conftest import assert_http_error
from tests.mocks.helpers import fqn
from tests.mocks.raw import CSRF_TOKEN, HTTP_401, SIGNED_TOKEN


LOADS = fqn(URLSafeTimedSerializer.loads)


def test_generate_tokens():
    token, signed = CSRFToken.generate_csrf_tokens()
    assert token and signed


def test_missing_cookie_token():
    with raises(Unauthorized) as info:
        CSRFToken.verify_csrf_token()
    assert_http_error(info, HTTP_401, TOKEN_COOKIE_ERROR)
    assert info.value.errors is None


def test_missing_header_token():
    with raises(Unauthorized) as info:
        CSRFToken.verify_csrf_token(SIGNED_TOKEN)
    assert_http_error(info, HTTP_401, TOKEN_HEADER_ERROR)
    assert info.value.errors is None


def test_invalid_token():
    with raises(Unauthorized) as info:
        CSRFToken.verify_csrf_token(SIGNED_TOKEN, "any")
    assert_http_error(info, HTTP_401, INVALID_TOKEN)
    assert info.value.errors[0]["type"] == fqn(ValidationError)
    assert info.value.errors[0]["detail"] and info.value.errors[1]


def test_signature_expired(mocker: Mocker):
    mock = mocker.patch(LOADS, side_effect=SignatureExpired("any"))
    with raises(Unauthorized) as info:
        CSRFToken.verify_csrf_token(SIGNED_TOKEN, CSRF_TOKEN)
    assert_http_error(info, HTTP_401, EXPIRED_TOKEN)
    mock.assert_called_once_with(SIGNED_TOKEN, MAX_AGE)
    assert info.value.errors[0]["type"] == fqn(SignatureExpired)
    assert info.value.errors[0]["detail"] == "any"


def test_bad_signature():
    with raises(Unauthorized) as info:
        CSRFToken.verify_csrf_token("any", CSRF_TOKEN)
    assert_http_error(info, HTTP_401, TOKEN_SIGNATURE_ERROR)
    assert info.value.errors[0]["type"] == fqn(BadSignature)
    assert info.value.errors[0]["detail"]


def test_incorrect(mocker: Mocker):
    mock = mocker.patch(LOADS, return_value="any")
    with raises(Unauthorized) as info:
        CSRFToken.verify_csrf_token(SIGNED_TOKEN, CSRF_TOKEN)
    assert_http_error(info, HTTP_401, INVALID_TOKEN)
    assert info.value.errors is None
    mock.assert_called_once_with(SIGNED_TOKEN, MAX_AGE)


def test_ok():
    CSRFToken.verify_csrf_token(SIGNED_TOKEN, CSRF_TOKEN)
