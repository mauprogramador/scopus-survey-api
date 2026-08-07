import secrets
from typing import Annotated

import fastapi
from itsdangerous import (
    BadData,
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)
from pydantic import TypeAdapter, ValidationError

from src.core.domain.types import ExcMsg
from src.infra.config.config import ENV, MAX_AGE, SALT
from src.infra.exceptions import CSRFAuthenticationError
from src.infra.types import CSRFToken


_SERIALIZER = URLSafeTimedSerializer(ENV.secret_key, SALT)
_TOKEN_ADAPTER: TypeAdapter[CSRFToken] = TypeAdapter(CSRFToken)

_COOKIE = fastapi.Cookie(
    alias="csrf-token",
    validation_alias="signed_token",
    include_in_schema=False,
)
_HEADER = fastapi.Header(
    alias="X-CSRF-Token",
    validation_alias="header_token",
    include_in_schema=False,
)


def generate_csrf_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(nbytes=48)
    signed = _SERIALIZER.dumps(token)
    return token, signed


def verify_csrf_token(
    signed_token: Annotated[str | None, _COOKIE] = None,
    header_token: Annotated[str | None, _HEADER] = None,
) -> None:

    if signed_token is None:
        raise CSRFAuthenticationError(ExcMsg.TOKEN_COOKIE_ERROR)

    if header_token is None:
        raise CSRFAuthenticationError(ExcMsg.TOKEN_HEADER_ERROR)

    try:
        _TOKEN_ADAPTER.validate_strings(header_token, strict=True)
    except ValidationError as exc:
        raise CSRFAuthenticationError(ExcMsg.INVALID_TOKEN, exc) from exc

    try:
        cookie_token: str = _SERIALIZER.loads(signed_token, MAX_AGE)

    except SignatureExpired as exc:
        raise CSRFAuthenticationError(ExcMsg.EXPIRED_TOKEN, exc) from exc

    except (BadSignature, BadData) as exc:
        raise CSRFAuthenticationError(
            ExcMsg.TOKEN_SIGNATURE_ERROR, exc
        ) from exc

    if header_token != cookie_token:
        raise CSRFAuthenticationError(ExcMsg.INVALID_TOKEN)
