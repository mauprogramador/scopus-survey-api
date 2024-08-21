from typing import Annotated

from fastapi import Request
from pydantic import ValidationError

from app.core.common.messages import INVALID_ACCESS_TOKEN, MISSING_ACCESS_TOKEN
from app.core.common.types import Token
from app.core.config.config import LOG, TOKEN, TOKEN_HEADER
from app.framework.exceptions import Unauthorized
from app.framework.fastapi.types import TokenHeader


class AccessToken:
    """Get and validate the access token"""

    def __init__(self) -> None:
        """Get and validate the access token"""

    async def __call__(
        self,
        request: Request,
        access_token: Annotated[str | None, TokenHeader] = None,
    ) -> None:
        if not access_token:
            access_token = request.headers.get(TOKEN_HEADER)

            if not access_token:
                raise Unauthorized(MISSING_ACCESS_TOKEN)

        try:
            Token.validate_strings(access_token)
        except ValidationError as error:
            raise Unauthorized(INVALID_ACCESS_TOKEN) from error

        if access_token != TOKEN:
            raise Unauthorized(INVALID_ACCESS_TOKEN)

        LOG.debug({"token": access_token})
