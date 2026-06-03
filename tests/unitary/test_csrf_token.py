from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic_core import ValidationError
from pytest import raises
from pytest_mock import MockerFixture as Mocker

from src.core.config.config import MAX_AGE
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import Unauthorized
from src.framework.fastapi.csrf_token import CSRFToken
from tests.conftest import assert_http_error
from tests.mocks.helpers import Patch, fqn
from tests.mocks.raw import CSRF_TOKEN, HTTP_401, SIGNED_TOKEN


LOADS = Patch(URLSafeTimedSerializer.loads)


def test_generate_tokens():
    token, signed = CSRFToken.generate_csrf_tokens()
    assert token and signed


def test_missing_cookie_token():
    with raises(Unauthorized) as info:
        CSRFToken.verify_csrf_token()
    assert_http_error(info, HTTP_401, ExcMsg.TOKEN_COOKIE_ERROR)
    assert info.value.errors is None


def test_missing_header_token():
    with raises(Unauthorized) as info:
        CSRFToken.verify_csrf_token(SIGNED_TOKEN)
    assert_http_error(info, HTTP_401, ExcMsg.TOKEN_HEADER_ERROR)
    assert info.value.errors is None


def test_invalid_token():
    with raises(Unauthorized) as info:
        CSRFToken.verify_csrf_token(SIGNED_TOKEN, "any")
    assert_http_error(info, HTTP_401, ExcMsg.INVALID_TOKEN)
    assert info.value.errors[0]["type"] == fqn(ValidationError)
    assert info.value.errors[0]["message"] and info.value.errors[1]


def test_signature_expired(mocker: Mocker):
    mock = mocker.patch(**LOADS(SignatureExpired("any")))
    with raises(Unauthorized) as info:
        CSRFToken.verify_csrf_token(SIGNED_TOKEN, CSRF_TOKEN)
    assert_http_error(info, HTTP_401, ExcMsg.EXPIRED_TOKEN)
    mock.assert_called_once_with(SIGNED_TOKEN, MAX_AGE)
    assert info.value.errors[0]["type"] == fqn(SignatureExpired)
    assert info.value.errors[0]["message"] == "any"


def test_bad_signature():
    with raises(Unauthorized) as info:
        CSRFToken.verify_csrf_token("any", CSRF_TOKEN)
    assert_http_error(info, HTTP_401, ExcMsg.TOKEN_SIGNATURE_ERROR)
    assert info.value.errors[0]["type"] == fqn(BadSignature)
    assert info.value.errors[0]["message"]


def test_incorrect(mocker: Mocker):
    mock = mocker.patch(**LOADS("any"))
    with raises(Unauthorized) as info:
        CSRFToken.verify_csrf_token(SIGNED_TOKEN, CSRF_TOKEN)
    assert_http_error(info, HTTP_401, ExcMsg.INVALID_TOKEN)
    assert info.value.errors is None
    mock.assert_called_once_with(SIGNED_TOKEN, MAX_AGE)


def test_verify():
    token, signed = CSRFToken.generate_csrf_tokens()
    CSRFToken.verify_csrf_token(signed, token)
