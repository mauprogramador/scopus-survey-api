from typing import Annotated

from fastapi import Header, Request

from app.core.config import OPENAPI_EXAMPLE, TOKEN, TOKEN_PATTERN
from app.exceptions import Unauthorized


class AccessToken:
    TOKEN_HEADER = Header(
        alias='X-Access-Token',
        description='The Validation Access Token',
        min_length=32,
        max_length=32,
        pattern=TOKEN_PATTERN,
        openapi_examples=OPENAPI_EXAMPLE,
    )

    async def __call__(
        self,
        request: Request,
        access_token: Annotated[str | None, TOKEN_HEADER] = None,
    ) -> None:
        if access_token:
            if access_token != TOKEN:
                raise Unauthorized('Invalid access token')
            return None

        access_token_header = request.headers.get('X-Access-Token')

        if not access_token_header:
            raise Unauthorized('No access token provided')

        if access_token_header != TOKEN:
            raise Unauthorized('Invalid access token')
