from typing import Annotated, Any, TypeAlias

from fastapi import Request
from pydantic import Field, TypeAdapter

from app.core.common.patterns import TOKEN_PATTERN

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
