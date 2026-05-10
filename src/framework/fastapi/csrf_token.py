from secrets import token_urlsafe
from typing import Annotated

from fastapi import Cookie, Header
from fastapi.openapi.models import Example
from itsdangerous import (
    BadData,
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)
from pydantic import ValidationError

from src.core.common.error_messages import (
    EXPIRED_TOKEN,
    INVALID_TOKEN,
    TOKEN_COOKIE_ERROR,
    TOKEN_HEADER_ERROR,
    TOKEN_SIGNATURE_ERROR,
)
from src.core.common.types import Token
from src.core.config.config import ENV, MAX_AGE, SALT
from src.core.domain.http_exceptions import Unauthorized


class CSRFToken:
    _SERIALIZER = URLSafeTimedSerializer(ENV.secret_key, SALT)
    _OPENAPI_EXAMPLE = {
        "CSRF Token": Example(
            summary="CSRF Token",
            description="Automatically managed by the client-side",
            value="c1d0cf66f682...",
        )
    }
    _COOKIE = Cookie(
        alias="csrf-token",
        validation_alias="signed_token",
        description="Cookies CSRF Token",
        openapi_examples=_OPENAPI_EXAMPLE,
    )
    _HEADER = Header(
        alias="X-CSRF-Token",
        validation_alias="header_token",
        description="Header CSRF Token",
        openapi_examples=_OPENAPI_EXAMPLE,
    )

    @classmethod
    def generate_csrf_tokens(cls) -> tuple[str, str]:
        token = token_urlsafe(nbytes=48)
        signed = cls._SERIALIZER.dumps(token)
        return token, signed

    @classmethod
    def verify_csrf_token(
        cls,
        signed_token: Annotated[str | None, _COOKIE] = None,
        header_token: Annotated[str | None, _HEADER] = None,
    ) -> None:

        if signed_token is None:
            raise Unauthorized(TOKEN_COOKIE_ERROR)

        if header_token is None:
            raise Unauthorized(TOKEN_HEADER_ERROR)

        try:
            Token.validate_strings(header_token, strict=True)
        except ValidationError as exc:
            raise Unauthorized(INVALID_TOKEN, exc) from exc

        try:
            cookie_token: str = cls._SERIALIZER.loads(signed_token, MAX_AGE)

        except SignatureExpired as exc:
            raise Unauthorized(EXPIRED_TOKEN, exc) from exc

        except (BadSignature, BadData) as exc:
            raise Unauthorized(TOKEN_SIGNATURE_ERROR, exc) from exc

        if header_token != cookie_token:
            raise Unauthorized(INVALID_TOKEN)
