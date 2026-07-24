import io
import random
from collections.abc import Callable
from http import HTTPMethod, HTTPStatus
from types import FunctionType
from typing import Any, Self
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import aiohttp_retry as aioretry
import httpx
import pandas as pd
from pandas import DataFrame

from src.core.common.types import Json, ResponseBundle
from src.core.config.scopus import MAX_ITEMS_PER_PAGE
from src.core.domain.translations import translate_error
from tests.mocks.raw import (
    HTTP_200,
    RAW_ENTRY,
    RAW_HEADERS_OK,
    REQUEST,
    RESET,
    SCOPUS_ID,
)


Target = type | FunctionType | Callable


def fqn(target: Target, method: Target = None, altname: str = None) -> str:
    """Gets the Fully Qualified Name for mocker.patch target"""
    if method is None:
        return f"{target.__module__}.{target.__qualname__}"

    if altname is not None:
        return f"{target.__module__}.{altname}.{method.__name__}"

    return f"{target.__module__}.{method.__name__}"


def spec(target: Target, method: Target = None, altname: str = None) -> Json:
    """Gets F.Q.N. for mocker.patch target and spec"""
    if method is None:
        return {"target": fqn(target), "spec": target}
    return {"target": fqn(target, method, altname), "spec": method}


def trans(exc: Exception) -> str:
    return translate_error(REQUEST, exc)


def load_csv_from_response(res: httpx.Response) -> DataFrame:
    """Load DataFrame from CSV file response ignoring metadata"""
    buffer_data = io.StringIO(res.content.decode())
    return pd.read_csv(
        buffer_data, sep=";", skiprows=(0, 1, 2, 3), keep_default_na=False
    )


def search_raw(total_results: int, entry_count: int | None = None) -> Json:
    """Build a raw search response"""
    items_per_page = min(total_results, MAX_ITEMS_PER_PAGE)
    count = items_per_page if entry_count is None else entry_count
    return {
        "search-results": {
            "opensearch:totalResults": str(total_results),
            "opensearch:itemsPerPage": str(items_per_page),
            "entry": [RAW_ENTRY] * count,
        }
    }


def abstract_raw(
    title: str | None = None,
    author: str | None = None,
    date: str | None = None,
) -> Json:
    """Build a raw abstract response"""
    return {
        "abstracts-retrieval-response": {
            "coredata": {
                "dc:identifier": SCOPUS_ID,
                "dc:title": title if title else "any_title",
                "prism:doi": f"10.{random.randint(1111, 9999)}0/any",
                "prism:coverDate": date if date else "any_date",
                "dc:creator": {
                    "author": [
                        {"ce:indexed-name": author if author else "any_author"}
                    ]
                },
            }
        }
    }


def headers_raw(remaining: int) -> dict[str, str]:
    """Build a raw response headers"""
    return {
        "X-RateLimit-Limit": "20000",
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(RESET),
        "X-ELS-Status": "OK",
    }


def response_mock(
    value: Json | None | Exception,
    status: HTTPStatus | None = None,
    headers: dict[str, str] | None = None,
) -> MagicMock:
    """Mock AIOHTTP ClientResponse"""
    if isinstance(value, dict) or value is None:
        json = AsyncMock(type(value).__qualname__, return_value=value)
    else:
        json = AsyncMock(type(value).__qualname__, side_effect=value)
    return MagicMock(
        spec=aiohttp.ClientResponse,
        status=status if status else HTTP_200,
        method=HTTPMethod.GET,
        headers=headers if headers else RAW_HEADERS_OK,
        json=json,
        text=AsyncMock(return_value=str(value)),
    )


def bundle_mock(
    value: Json,
    status: HTTPStatus | None = None,
    headers: dict[str, str] | None = None,
) -> ResponseBundle:
    """Mock ResponseBundle"""
    return ResponseBundle(
        code=status if status else HTTP_200,
        headers=headers if headers else RAW_HEADERS_OK,
        data=value,
    )


def get_patch(value: Any | list[Any] | Exception) -> tuple[str, AsyncMock]:
    """Patch AIOHTTP Retry.get"""
    if isinstance(value, (list, BaseException)):
        new = AsyncMock(aiohttp.ClientResponse, side_effect=value)
    else:
        new = AsyncMock(aiohttp.ClientResponse, return_value=value)
    return fqn(aioretry.RetryClient.get), new


class Patch:
    """Context for mocker.patch params
    Args:
        method: Type | FunctionType | Callable
        altname: str
        value: Exception | Any
    """

    _VALUE_KEYS = ("side_effect", "return_value")

    def __init__(self, target: Target, *args: Any) -> None:
        """Context for mocker.patch params
        Args:
            method: Type | FunctionType | Callable
            altname: str
            value: Exception | Any
        """

        self._keys = ["target", "spec"]
        self.target: str = None
        self.spec: Target = None
        self.side_effect: Any = None
        self.return_value: Any = None

        method: Target | None = None
        value: Exception | Any = None
        altname: str | None = None

        for arg in args:
            if isinstance(arg, Target):
                method = arg
            elif isinstance(arg, str):
                altname = arg
            else:
                value = arg

        self.target = fqn(target, method, altname)
        self.spec = target if method is None else method
        self._handle_value(value)

    def _handle_value(self, value: Exception | Any) -> None:
        if value is None:
            return None

        if isinstance(value, (list, BaseException)):
            self.side_effect = value
            self.return_value = None
        else:
            self.return_value = value
            self.side_effect = None

        for key in self._VALUE_KEYS:
            key_attr_value = getattr(self, key)

            if key_attr_value is not None and key not in self._keys:
                self._keys.append(key)

            elif key_attr_value is None and key in self._keys:
                self._keys.remove(key)

        return None

    def keys(self) -> list[str]:
        return self._keys

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __call__(self, value: Exception | Any) -> Self:
        self._handle_value(value)
        return self


class MockAsyncContext:
    """Mock async contexts `async with`"""

    def __call__(self, *args: Any, **kwds: Any) -> Self:
        return self

    async def __await__(self):
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
