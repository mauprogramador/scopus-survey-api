from hashlib import sha1

from fastapi import Request
from itsdangerous import (
    BadData,
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)
from pydantic import ValidationError

from src.core.common.messages import (
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

    @classmethod
    def generate_csrf_tokens(cls) -> tuple[str, str]:
        token = sha1(TOKEN.encode(encoding="utf-8")).hexdigest()
        signed = cls.__SERIALIZER.dumps(token)
        return token, signed

    @classmethod
    def verify_csrf_token(
        cls, request: Request, csrf_token: str | None
    ) -> None:
        print(csrf_token)

        if not csrf_token:
            raise Unauthorized(MISSING_TOKEN)

        try:
            Token.validate_strings(csrf_token, strict=True)
        except ValidationError as exc:
            raise Unauthorized(INVALID_TOKEN, exc) from exc

        signed_token = request.cookies.get("csrf-token")
        if signed_token is None:
            raise Unauthorized(TOKEN_COOKIE_ERROR)
        print(signed_token)

        csrf_token_header = request.headers.get("X-CSRF-Token")
        if csrf_token_header is None or csrf_token_header != csrf_token:
            raise Unauthorized(TOKEN_HEADER_ERROR)
        print(csrf_token_header)

        csrf_token_session = request.session.get("csrf-token")
        if csrf_token_session is None or csrf_token_session != csrf_token:
            raise Unauthorized(TOKEN_SESSION_ERROR)
        print(csrf_token_session)

        try:
            csrf_cookie: str = cls.__SERIALIZER.loads(signed_token, MAX_AGE)

        except SignatureExpired as exc:
            raise Unauthorized(EXPIRED_TOKEN, exc) from exc

        except (BadSignature, BadData) as exc:
            raise Unauthorized(TOKEN_SIGNATURE_ERROR, exc) from exc

        if csrf_token != csrf_cookie:
            raise Unauthorized(INVALID_TOKEN)
