from typing import Annotated, Any, TypeAlias

from fastapi import Query
from pydantic import BaseModel, Field, TypeAdapter

from app.core.common.patterns import TOKEN_PATTERN, API_KEY_PATTERN


Token: TypeAdapter[str] = TypeAdapter(
    Annotated[str, Field(min_length=32, max_length=32, pattern=TOKEN_PATTERN)]
)

Articles: TypeAlias = list[dict[str, str]]

Errors: TypeAlias = list[dict[str, Any]] | None

APIKeyQuery = Annotated[
    str,
    Query(
        alias="apiKey",
        description="Your Scopus API Key",
        min_length=32,
        max_length=32,
        pattern=API_KEY_PATTERN,
    ),
]


class SearchParams(BaseModel):
    api_key: str
    keywords: list[str]


class LogConfig(BaseModel):
    host: str
    port: int
    logging_file: bool
    debug: bool


class Quota(BaseModel):
    limit: int
    remaining: int
    reset_datetime: str
    status: str
