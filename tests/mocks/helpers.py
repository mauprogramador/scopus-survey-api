import io
import random
from collections.abc import Callable
from http import HTTPMethod, HTTPStatus
from types import FunctionType
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import aiohttp_retry as aioretry
import httpx
import pandas as pd
from pandas import DataFrame

from src.adapters.types import ResponseBundle
from src.core.domain.types import Json
from src.infra.config.scopus import MAX_ITEMS_PER_PAGE
from src.infra.i18n.translations import translate_error
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


def patch(spec_data: Json, value: Exception | Any) -> Json:
    patch_data = spec_data.copy()
    if isinstance(value, (list, BaseException)):
        patch_data["side_effect"] = value
    else:
        patch_data["return_value"] = value
    return patch_data


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
