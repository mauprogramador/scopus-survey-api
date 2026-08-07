from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic_core import ValidationError
from pytest import raises
from pytest_mock import MockerFixture as Mocker

from src.core.domain.types import ExcMsg
from src.core.domain.exceptions import Unauthorized
from src.infra.config.config import MAX_AGE
from src.infra.fastapi.csrf_token import (
    generate_csrf_token,
    verify_csrf_token,
)
from tests.conftest import assert_http_error
from tests.mocks.helpers import Patch, fqn
from tests.mocks.raw import CSRF_TOKEN, HTTP_401, SIGNED_TOKEN


LOADS = Patch(URLSafeTimedSerializer.loads)


def test_generate_tokens():
    token, signed = generate_csrf_token()
    assert token and signed


def test_missing_cookie_token():
    with raises(Unauthorized) as info:
        verify_csrf_token()
    assert_http_error(info, HTTP_401, ExcMsg.TOKEN_COOKIE_ERROR)
    assert info.value.details is None


def test_missing_header_token():
    with raises(Unauthorized) as info:
        verify_csrf_token(SIGNED_TOKEN)
    assert_http_error(info, HTTP_401, ExcMsg.TOKEN_HEADER_ERROR)
    assert info.value.details is None


def test_invalid_token():
    with raises(Unauthorized) as info:
        verify_csrf_token(SIGNED_TOKEN, "any")
    assert_http_error(info, HTTP_401, ExcMsg.INVALID_TOKEN)
    assert info.value.details[0]["type"] == fqn(ValidationError)
    assert info.value.details[0]["message"]


def test_signature_expired(mocker: Mocker):
    mock = mocker.patch(**LOADS(SignatureExpired("any")))
    with raises(Unauthorized) as info:
        verify_csrf_token(SIGNED_TOKEN, CSRF_TOKEN)
    assert_http_error(info, HTTP_401, ExcMsg.EXPIRED_TOKEN)
    mock.assert_called_once_with(SIGNED_TOKEN, MAX_AGE)
    assert info.value.details[0]["type"] == fqn(SignatureExpired)
    assert info.value.details[0]["message"] == "any"


def test_bad_signature():
    with raises(Unauthorized) as info:
        verify_csrf_token("any", CSRF_TOKEN)
    assert_http_error(info, HTTP_401, ExcMsg.TOKEN_SIGNATURE_ERROR)
    assert info.value.details[0]["type"] == fqn(BadSignature)
    assert info.value.details[0]["message"]


def test_incorrect(mocker: Mocker):
    mock = mocker.patch(**LOADS("any"))
    with raises(Unauthorized) as info:
        verify_csrf_token(SIGNED_TOKEN, CSRF_TOKEN)
    assert_http_error(info, HTTP_401, ExcMsg.INVALID_TOKEN)
    assert info.value.details is None
    mock.assert_called_once_with(SIGNED_TOKEN, MAX_AGE)


def test_verify():
    token, signed = generate_csrf_token()
    verify_csrf_token(signed, token)
