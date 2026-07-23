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

from src.core.common.types import Token
from src.core.config.config import ENV, MAX_AGE, SALT
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import Unauthorized


_SERIALIZER = URLSafeTimedSerializer(ENV.secret_key, SALT)
_TOKEN_ADAPTER: TypeAdapter[Token] = TypeAdapter(Token)

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
        raise Unauthorized(ExcMsg.TOKEN_COOKIE_ERROR)

    if header_token is None:
        raise Unauthorized(ExcMsg.TOKEN_HEADER_ERROR)

    try:
        _TOKEN_ADAPTER.validate_strings(header_token, strict=True)
    except ValidationError as exc:
        raise Unauthorized(ExcMsg.INVALID_TOKEN, exc) from exc

    try:
        cookie_token: str = _SERIALIZER.loads(signed_token, MAX_AGE)

    except SignatureExpired as exc:
        raise Unauthorized(ExcMsg.EXPIRED_TOKEN, exc) from exc

    except (BadSignature, BadData) as exc:
        raise Unauthorized(ExcMsg.TOKEN_SIGNATURE_ERROR, exc) from exc

    if header_token != cookie_token:
        raise Unauthorized(ExcMsg.INVALID_TOKEN)
