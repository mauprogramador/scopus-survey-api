from http import HTTPStatus as codes
from unittest.mock import MagicMock, patch

from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from pytest import raises

from src.core.common.messages import (
    EXPIRED_TOKEN,
    INVALID_TOKEN,
    MISSING_TOKEN,
    TOKEN_COOKIE_ERROR,
    TOKEN_HEADER_ERROR,
    TOKEN_SESSION_ERROR,
    TOKEN_SIGNATURE_ERROR,
)
from src.core.config.config import MAX_AGE
from src.core.domain.http_exceptions import Unauthorized
from src.framework.fastapi.csrf_token import CSRFToken
from tests.conftest import assert_http_error
from tests.helpers.models import Request
from tests.mocks.common import CSRF_TOKEN, SIGNED_TOKEN


def test_generate_tokens():
    token, signed = CSRFToken.generate_csrf_tokens()
    assert token and signed


def test_missing_token():
    with raises(Unauthorized) as exc:
        CSRFToken.verify_csrf_token(Request(), None)
    assert_http_error(exc, codes.UNAUTHORIZED, MISSING_TOKEN, False)


def test_invalid_token():
    with raises(Unauthorized) as exc:
        CSRFToken.verify_csrf_token(Request(), "any")
    assert_http_error(exc, codes.UNAUTHORIZED, INVALID_TOKEN)


@patch.object(Request, "cookies", {"csrf-token": None})
def test_missing_cookie_token():
    with raises(Unauthorized) as exc:
        CSRFToken.verify_csrf_token(Request(), CSRF_TOKEN)
    assert_http_error(exc, codes.UNAUTHORIZED, TOKEN_COOKIE_ERROR, False)


@patch.object(Request, "cookies", {"csrf-token": "any"})
def test_missing_header_token():
    with raises(Unauthorized) as exc:
        CSRFToken.verify_csrf_token(
            Request(headers={"X-CSRF-Token": "any"}), CSRF_TOKEN
        )
    assert_http_error(exc, codes.UNAUTHORIZED, TOKEN_HEADER_ERROR, False)


@patch.object(Request, "cookies", {"csrf-token": "any"})
@patch.object(Request, "session", {"csrf-token": None})
def test_missing_session_token():
    with raises(Unauthorized) as exc:
        CSRFToken.verify_csrf_token(Request(CSRF_TOKEN), CSRF_TOKEN)
    assert_http_error(exc, codes.UNAUTHORIZED, TOKEN_SESSION_ERROR, False)


@patch.object(Request, "cookies", {"csrf-token": SIGNED_TOKEN})
@patch.object(Request, "session", {"csrf-token": CSRF_TOKEN})
@patch.object(
    URLSafeTimedSerializer,
    "loads",
    side_effect=SignatureExpired("any"),
)
def test_signature_expired(mock: MagicMock):
    with raises(Unauthorized) as exc:
        CSRFToken.verify_csrf_token(Request(CSRF_TOKEN), CSRF_TOKEN)
    assert_http_error(exc, codes.UNAUTHORIZED, EXPIRED_TOKEN)
    mock.assert_called_once_with(SIGNED_TOKEN, MAX_AGE)


@patch.object(Request, "cookies", {"csrf-token": "any"})
@patch.object(Request, "session", {"csrf-token": CSRF_TOKEN})
def test_bad_signature():
    with raises(Unauthorized) as exc:
        CSRFToken.verify_csrf_token(Request(CSRF_TOKEN), CSRF_TOKEN)
    assert_http_error(exc, codes.UNAUTHORIZED, TOKEN_SIGNATURE_ERROR)


@patch.object(Request, "cookies", {"csrf-token": SIGNED_TOKEN})
@patch.object(Request, "session", {"csrf-token": CSRF_TOKEN})
@patch.object(
    URLSafeTimedSerializer,
    "loads",
    return_value="any",
)
def test_incorrect(mock: MagicMock):
    with raises(Unauthorized) as exc:
        CSRFToken.verify_csrf_token(Request(CSRF_TOKEN), CSRF_TOKEN)
    assert_http_error(exc, codes.UNAUTHORIZED, INVALID_TOKEN, False)
    mock.assert_called_once_with(SIGNED_TOKEN, MAX_AGE)


@patch.object(Request, "cookies", {"csrf-token": SIGNED_TOKEN})
def test_ok():
    with patch.object(Request, "session", {"csrf-token": CSRF_TOKEN}) as mock:
        CSRFToken.verify_csrf_token(Request(CSRF_TOKEN), CSRF_TOKEN)
    assert mock.get("csrf-token") is None
