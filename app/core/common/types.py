from typing import Annotated, Any, TypeAlias

from pydantic import Field, TypeAdapter

from app.core.common.patterns import TOKEN_PATTERN


Token: TypeAdapter[str] = TypeAdapter(
    Annotated[str, Field(min_length=32, max_length=32, pattern=TOKEN_PATTERN)]
)

Articles: TypeAlias = list[dict[str, str]]

TomlSettings: TypeAlias = dict[str, bool | str | int]

Errors: TypeAlias = list[dict[str, Any]] | None
