from collections.abc import Coroutine
from typing import Annotated, Any, Literal

from pydantic import Field

from src.adapters.types import Headers


# e.g. 989a5e2a50389ae6a5faf4c271d8bfb30cbbd88c  (Random Hash)
type CSRFToken = Annotated[
    str, Field(pattern=r"^[a-zA-Z0-9\-\_]{64}$", min_length=64, max_length=64)
]

type APIName = Literal["search", "abstract"]

type FetcherTask[T] = Coroutine[Any, Any, tuple[T, Headers]]

type LogLevel = Literal[
    "DEBUG",
    "API_CALL",
    "INFO",
    "ACCESS",
    "QUOTA",
    "WARNING",
    "ERROR",
    "EXCEPTION",
]
