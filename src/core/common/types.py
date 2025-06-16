from typing import Annotated, Any, NamedTuple, Protocol, TypeAlias

from fastapi import HTTPException
from itsdangerous import BadData
from pydantic import Field, TypeAdapter, ValidationError
from requests import RequestException

from src.core.common.patterns import KEYWORD_PATTERN, TOKEN_PATTERN

Keyword: TypeAlias = Annotated[
    str, Field(pattern=KEYWORD_PATTERN, min_length=2, max_length=50)
]

Json: TypeAlias = dict[str, Any]

Translation: TypeAlias = dict[str, dict[str, str]]

Articles: TypeAlias = list[dict[str, str]]

Errors: TypeAlias = list[Json] | Json | None

ErrorTypes: TypeAlias = (
    Exception | HTTPException | ValidationError | RequestException | BadData
)

Token: TypeAdapter[str | None] = TypeAdapter(
    Annotated[
        str | None,
        Field(
            pattern=TOKEN_PATTERN,
            min_length=40,
            max_length=40,
        ),
    ]
)


class SearchParams(Protocol):
    api_key: str
    keywords: list[str]
    max_count: int
    ratio: int
    start_year: int
    end_year: int

    @property
    def year_range(self) -> str:
        pass


class LogParams(NamedTuple):
    host: str
    port: int
    logging_file: bool
    debug: bool


class Quota(Protocol):
    limit: int
    remaining: int
    reset_datetime: str
    status: str
