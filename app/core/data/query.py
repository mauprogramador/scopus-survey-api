from re import match
from typing import Annotated

from fastapi import Query, Depends
from fastapi.openapi.models import Example

from app.core.common.messages import (
    INVALID_ACCESS_TOKEN,
    INVALID_KEYWORD,
    INVALID_KEYWORDS_LENGTH,
    MISSING_ACCESS_TOKEN,
    MISSING_API_KEY,
    MISSING_KEYWORDS,
)
from app.core.common.patterns import (
    API_KEY_PATTERN,
    KEYWORD_PATTERN,
    TOKEN_PATTERN,
)
from app.core.config.config import TOKEN_HEADER, TOKEN
from app.core.config.scopus import CURRENT_YEAR, LAST_DECADE, LAST_THREE_YEARS
from app.core.common.types import APIKeyQuery
from app.core.domain.http_exceptions import Unauthorized, UnprocessableContent


DESCRIPTION = (
    f"The value of the `{TOKEN_HEADER}` header will be "
    "set automatically, you **should not** change it"
)
OPENAPI_EXAMPLE = {
    "Token": Example(
        summary="Access Token", description=DESCRIPTION, value=TOKEN
    )
}


class APIKeyParam:

    def __init__(
        self,
        api_key: APIKeyQuery,
    ) -> None:
        self.api_key = api_key


class CSVParams:

    def __init__(
        self,
        api_key: APIKeyQuery,
        csrf_token: Annotated[
            str,
            Query(
                description="The validation CSRF Token",
                min_length=32,
                max_length=32,
                pattern=TOKEN_PATTERN,
                # examples=OPENAPI_EXAMPLE,
            ),
        ] = None,
    ) -> None:
        if csrf_token is None:
            raise Unauthorized(MISSING_ACCESS_TOKEN)

        if csrf_token != TOKEN:
            raise Unauthorized(INVALID_ACCESS_TOKEN)

        if api_key is None:
            raise Unauthorized(MISSING_API_KEY)

        self.api_key = api_key
        self.csrf_token = csrf_token


class SearchParams:

    def __init__(
        self,
        api_key: APIKeyQuery,
    ) -> None:
        self.api_key = api_key

    # keywords: list[str] = Field(
    #     default=None,
    #     description="Keywords to search for in the articles",
    #     min_length=1,
    #     max_length=4,
    # )
    # count: int = Field(
    #     default=50,
    #     description="Limits the number of returned articles",
    #     ge=1,
    #     le=200,
    # )
    # ratio: int = Field(
    #     default=80,
    #     description="Filters and removes similar articles",
    #     ge=0,
    #     le=100,
    # )
    # start_year: int = Field(
    #     default=LAST_THREE_YEARS,
    #     description="Start of search date range",
    #     ge=LAST_DECADE,
    #     le=(CURRENT_YEAR - 1),
    # )
    # end_year: int = Field(
    #     default=CURRENT_YEAR,
    #     description="End of search date range",
    #     ge=(LAST_DECADE + 1),
    #     le=CURRENT_YEAR,
    # )

    # @model_validator(mode="after")
    # def verify_keywords(self) -> Self:

    #     if not self.keywords:
    #         raise UnprocessableContent(MISSING_KEYWORDS)

    #     if len(self.keywords) == 1:
    #         self.keywords = self.keywords[0].split(",")

    #     if len(self.keywords) < 2:
    #         raise UnprocessableContent(INVALID_KEYWORDS_LENGTH)

    #     for keyword in self.keywords:
    #         if not match(KEYWORD_PATTERN, keyword):
    #             raise UnprocessableContent(INVALID_KEYWORD)

    #     return self
