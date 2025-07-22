from hashlib import sha1
from typing import Annotated

from fastapi import Cookie, Header, Query, Request
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
    MISSING_TOKEN,
    TOKEN_COOKIE_ERROR,
    TOKEN_HEADER_ERROR,
    TOKEN_SESSION_ERROR,
    TOKEN_SIGNATURE_ERROR,
)
from src.core.common.types import Token
from src.core.config.config import MAX_AGE, SALT, SECRET_KEY, TOKEN
from src.core.domain.http_exceptions import Unauthorized


class CSRFToken:
    __SERIALIZER = URLSafeTimedSerializer(SECRET_KEY, SALT)
    __OPENAPI_EXAMPLE = {
        "CSRF Token": Example(
            summary="CSRF Token",
            description="Automatically managed by the client-side",
            value="c1d0cf66f682...",
        )
    }
    __Query = Query(
        alias="csrfToken",
        validation_alias="query_token",
        description="Query params CSRF Token",
        openapi_examples=__OPENAPI_EXAMPLE,
    )
    __Cookie = Cookie(
        alias="csrf-token",
        validation_alias="signed_token",
        description="Cookies CSRF Token",
        openapi_examples=__OPENAPI_EXAMPLE,
    )
    __Header = Header(
        alias="X-CSRF-Token",
        validation_alias="header_token",
        description="Header CSRF Token",
        openapi_examples=__OPENAPI_EXAMPLE,
    )

    @classmethod
    def generate_csrf_tokens(cls) -> tuple[str, str]:
        token = sha1(TOKEN.encode(encoding="utf-8")).hexdigest()
        signed = cls.__SERIALIZER.dumps(token)
        return token, signed

    @classmethod
    def verify_csrf_token(
        cls,
        request: Request,
        query_token: Annotated[str | None, __Query] = None,
        signed_token: Annotated[str | None, __Cookie] = None,
        header_token: Annotated[str | None, __Header] = None,
    ) -> None:
        print(query_token)

        if not query_token:
            raise Unauthorized(MISSING_TOKEN)

        try:
            Token.validate_strings(query_token, strict=True)
        except ValidationError as exc:
            raise Unauthorized(INVALID_TOKEN, exc) from exc

        if signed_token is None:
            raise Unauthorized(TOKEN_COOKIE_ERROR)
        print(signed_token)

        if header_token is None or header_token != query_token:
            raise Unauthorized(TOKEN_HEADER_ERROR)
        print(header_token)

        token_session = request.session.get("csrf-token")
        if token_session is None or token_session != query_token:
            raise Unauthorized(TOKEN_SESSION_ERROR)
        print(token_session)

        try:
            token_cookie: str = cls.__SERIALIZER.loads(signed_token, MAX_AGE)

        except SignatureExpired as exc:
            raise Unauthorized(EXPIRED_TOKEN, exc) from exc

        except (BadSignature, BadData) as exc:
            raise Unauthorized(TOKEN_SIGNATURE_ERROR, exc) from exc

        if query_token != token_cookie:
            raise Unauthorized(INVALID_TOKEN)
