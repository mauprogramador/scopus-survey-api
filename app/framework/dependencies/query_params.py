from typing import Annotated, Self

from fastapi import Request

from app.core.common.messages import (
    INVALID_KEYWORD,
    INVALID_KEYWORDS_LENGTH,
    MISSING_API_KEY,
    MISSING_KEYWORDS,
)
from app.core.common.patterns import KEYWORD_PATTERN
from app.core.common.types import Keywords
from app.core.config.config import API_KEY_HEADER, KEYWORDS_HEADER, LOG
from app.framework.exceptions import Unauthorized, UnprocessableContent
from app.framework.fastapi.types import APIKeyQuery, KeywordsQuery


class QueryParams:
    """Get and validate the query params"""

    def __init__(self) -> None:
        """Get and validate the query params"""
        self.api_key: str = None
        self.keywords: Keywords = None

    def equals(self, api_key: str, keywords: list[str]) -> bool:
        return (self.api_key, self.keywords) == (api_key, keywords)

    def to_dict(self) -> dict[str, str | Keywords]:
        return {"api_key": self.api_key, "keywords": self.keywords}

    async def __call__(
        self,
        request: Request,
        api_key: Annotated[str | None, APIKeyQuery] = None,
        keywords: Annotated[Keywords | None, KeywordsQuery] = None,
    ) -> Self:
        if not api_key:
            api_key = request.query_params.get(API_KEY_HEADER)

            if not api_key:
                raise Unauthorized(MISSING_API_KEY)

        self.api_key = api_key
        LOG.debug({"api_key": api_key})

        if not keywords:
            keywords = request.query_params.getlist(KEYWORDS_HEADER)

            if not keywords:
                raise UnprocessableContent(MISSING_KEYWORDS)

        if len(keywords) == 1:
            keywords = keywords[0].split(",")

        if len(keywords) < 2:
            raise UnprocessableContent(INVALID_KEYWORDS_LENGTH)

        for keyword in keywords:
            if not KEYWORD_PATTERN.match(keyword):
                raise UnprocessableContent(INVALID_KEYWORD)

        self.keywords = keywords
        LOG.debug({"keywords": keywords})

        return self
