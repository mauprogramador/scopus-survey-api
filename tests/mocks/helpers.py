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
from tests.mocks.raw import (
    CSV_FILE_NAME,
    HTTP_200,
    RAW_ENTRY,
    RAW_HEADERS_OK,
    SCOPUS_ID,
    SKIPROWS,
)


def fqn(
    target: MethodType | Type[Any], method_name: MethodType | str = None
) -> str:
    """Gets the Fully Qualified Name"""
    if not method_name:
        return f"{target.__module__}.{target.__qualname__}"
    if isinstance(method_name, str):
        return f"{target.__module__}.{method_name}"
    return f"{target.__module__}.{method_name.__qualname__}"


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


def load_csv_file_response_dataframe(response: Response) -> DataFrame:
    """Load DataFrame from CSV file response ignoring metadata"""
    buffer_data = StringIO(response.content.decode())
    return read_csv(
        buffer_data, sep=";", skiprows=SKIPROWS, keep_default_na=False
    )


def search_raw(total_results: int, entry_count: int | None = None) -> Json:
    """Build a raw search response"""
    items_per_page = min(total_results, 25)
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
