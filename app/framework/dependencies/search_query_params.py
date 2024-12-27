from typing import Annotated, Self

from fastapi import Request

from app.core.common.messages import (
    INVALID_KEYWORD,
    INVALID_KEYWORDS_LENGTH,
    MISSING_API_KEY,
    MISSING_KEYWORDS,
)
from app.core.common.patterns import KEYWORD_PATTERN
from app.core.config.config import API_KEY_QUERY, KEYWORDS_QUERY, LOG
from app.framework.exceptions import Unauthorized, UnprocessableContent
from app.framework.fastapi.types import (
    APIKeyQuery,
    KeywordsQuery,
    CountQuery,
    ThresholdQuery,
    StartYearQuery,
    EndYearQuery
)


class SearchQueryParams:
    """Get and validate the query params"""

    def __init__(self) -> None:
        """Get and validate the query params"""
        self.__api_key: str = None
        self.__keywords: list[str] = None

    @property
    def values(self) -> tuple[str, list[str]]:
        return self.__api_key, self.__keywords

    @property
    def items(self) -> dict[str, str | list[str]]:
        return {"api_key": self.__api_key, "keywords": self.__keywords}

    async def __call__(
        self,
        request: Request,
        api_key: Annotated[str | None, APIKeyQuery] = None,
        keywords: Annotated[list[str] | None, KeywordsQuery] = None,
        count: Annotated[int | None, CountQuery] = None,
        threshold: Annotated[int | None, ThresholdQuery] = None,
        start_year: Annotated[int | None, StartYearQuery] = None,
        end_year: Annotated[int | None, EndYearQuery] = None
    ) -> Self:
        if not api_key:
            api_key = request.query_params.get(API_KEY_QUERY)

            if not api_key:
                raise Unauthorized(MISSING_API_KEY)

        self.__api_key = api_key
        LOG.debug({"api_key": api_key})

        if not keywords:
            keywords = request.query_params.getlist(KEYWORDS_QUERY)

            if not keywords:
                raise UnprocessableContent(MISSING_KEYWORDS)

        if len(keywords) == 1:
            keywords = keywords[0].split(",")

        if len(keywords) < 2:
            raise UnprocessableContent(INVALID_KEYWORDS_LENGTH)

        for keyword in keywords:
            if not KEYWORD_PATTERN.match(keyword):
                raise UnprocessableContent(INVALID_KEYWORD)

        self.__keywords = keywords
        LOG.debug({"keywords": keywords})

        return self
