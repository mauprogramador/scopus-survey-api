from http import HTTPMethod, HTTPStatus
from io import StringIO
from random import randint
from types import MethodType
from typing import Any, Type
from unittest.mock import AsyncMock, MagicMock

from aiohttp import ClientResponse
from fastapi.responses import FileResponse, JSONResponse
from httpx import Response
from pandas import DataFrame, read_csv

from src.core.common.types import CombinationBundle, Json
from src.core.config.config import DIRECTORY
from src.core.config.scopus import MAX_ITEMS_PER_PAGE
from src.core.data.quota_results_handler import QuotaResultsHandler
from src.core.data.serializers import ScopusSearch
from tests.mocks.raw import (
    CSV_FILE_NAME,
    HTTP_200,
    RAW_ENTRY,
    RAW_HEADERS_OK,
    SCOPUS_ID,
    SKIPROWS,
)


Target: TypeAlias = Type | MethodType | FunctionType | Callable


def fqn(target: Target, method: Target = None) -> str:
    """Gets the Fully Qualified Name"""
    if method is None:
        return f"{target.__module__}.{target.__qualname__}"

    if isinstance(method, MethodType):
        class_name = method.__self__.__class__.__name__
        method_name = method.__name__
        return f"{target.__module__}.{class_name}.{method_name}"

    if isinstance(method, (Type, FunctionType, Callable)):
        return f"{target.__module__}.{method.__name__}"

    if hasattr(method, "__name__"):
        return f"{target.__module__}.{method.__name__}"

    return f"{target.__module__}.{method.__class__.__name__}"


def mock_combination_url(*_) -> CombinationBundle:
    """Mock URLBuilder.combination_url"""
    return CombinationBundle(combination="any", url="any")


async def mock_survey_totals_found(
    bundles_map: dict[int, CombinationBundle],
) -> list[Json]:
    """Mock ScopusSearchAPI.survey_totals_found"""
    for index in bundles_map.keys():
        bundles_map[index].total = randint(16, 256)
    return [bundle.model_dump() for bundle in bundles_map.values()]


def mock_filter(dataframe: DataFrame, *_) -> DataFrame:
    """Mock ArticlesSimilarityFilter.filter"""
    return dataframe


async def mock_survey_combinations(*_) -> JSONResponse:
    """Mock KeywordCombinationFinder.survey_combinations"""
    return JSONResponse({"Any": "any"})


async def mock_retrieve_articles(*_) -> FileResponse:
    """Mock ScopusArticlesAggregator.retrieve_articles"""
    return FileResponse(DIRECTORY / CSV_FILE_NAME)


def mock_from_iterable(*_) -> tuple[str, ...]:
    """Mock itertools.chain.from_iterable"""
    return ("Python",)


def load_csv_from_response(response: Response) -> DataFrame:
    """Load DataFrame from CSV file response ignoring metadata"""
    buffer_data = StringIO(response.content.decode())
    return read_csv(
        buffer_data, sep=";", skiprows=SKIPROWS, keep_default_na=False
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
) -> dict[str, Any]:
    """Build a raw abstract response"""
    return {
        "abstracts-retrieval-response": {
            "coredata": {
                "dc:identifier": SCOPUS_ID,
                "dc:title": title if title else "any_title",
                "prism:doi": f"10.{randint(1111, 9999)}0/any",
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
        json = AsyncMock(return_value=value)
    else:
        json = AsyncMock(side_effect=value)
    return MagicMock(
        spec=ClientResponse,
        status=status if status else HTTP_200,
        method=HTTPMethod.GET,
        headers=headers if headers else RAW_HEADERS_OK,
        json=json,
    )


def results_mock(total_results: int) -> QuotaResultsHandler:
    """Builds a QuotaResultsHandler instance"""
    first_search = ScopusSearch(**search_raw(total_results))
    return QuotaResultsHandler(first_search)
