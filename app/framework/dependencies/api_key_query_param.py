from typing import Annotated

from fastapi import Request

from app.core.config.config import API_KEY_QUERY, LOG
from app.framework.fastapi.types import APIKeyQuery


class APIKeyQueryParam:
    """Get and validate the API Key query param"""

    def __init__(self) -> None:
        """Get and validate the API Key query param"""
        self.__api_key: str | None = None

    async def __call__(
        self,
        request: Request,
        api_key: Annotated[str | None, APIKeyQuery] = None,
    ) -> str | None:
        if not api_key:
            api_key = request.query_params.get(API_KEY_QUERY)

        self.__api_key = api_key
        LOG.debug({"api_key": api_key})

        return self.__api_key
