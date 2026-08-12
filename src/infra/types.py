from collections.abc import Coroutine
from typing import Annotated, Any, Literal

from pydantic import Field

from src.adapters.types import Headers


# e.g. 989a5e2a50389ae6a5faf4c271d8bfb30cbbd88c  (Random Hash)
_TOKEN_PATTERN = r"^[a-zA-Z0-9\-\_]{64}$"

type CSRFToken = Annotated[
    str, Field(pattern=_TOKEN_PATTERN, min_length=64, max_length=64)
]

type APIName = Literal["search", "abstract"]

type FetcherTask[T] = Coroutine[Any, Any, tuple[T, Headers]]
