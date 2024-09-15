from typing import Annotated, Any, TypeAlias

from fastapi import Request
from pydantic import BaseModel, Field, TypeAdapter, field_validator

from app.core.common.messages import INVALID_KEYWORD
from app.core.common.patterns import (
    API_KEY_PATTERN,
    KEYWORD_PATTERN,
    TOKEN_PATTERN,
)

Keywords: TypeAlias = list[str]

Headers: TypeAlias = dict[str, str]

Articles: TypeAlias = list[dict[str, str]]

Table: TypeAlias = list[list[str]] | None

Context: TypeAlias = tuple[Request, str, dict[str, Any]]

TomlSettings: TypeAlias = dict[str, bool | str | int]

PyprojectTool: TypeAlias = dict[str, Any]

Poetry: TypeAlias = dict[str, str | list[str]]

Errors: TypeAlias = list[dict[str, Any]] | None

Token = TypeAdapter(
    Annotated[str, Field(min_length=32, max_length=32, pattern=TOKEN_PATTERN)]
)


class SearchParams(BaseModel):
    """Type validator for APIKey and Keywords search params"""

    api_key: str = Field(min_length=32, max_length=32, pattern=API_KEY_PATTERN)
    keywords: Keywords = Field(min_length=2, max_length=4)

    @field_validator("keywords")
    @classmethod
    def validate_keywords(cls, keywords: Keywords) -> Keywords:
        for keyword in keywords:
            if not KEYWORD_PATTERN.match(keyword):
                raise ValueError(INVALID_KEYWORD)
        return keywords
