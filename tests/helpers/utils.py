from io import StringIO
from json import loads
from types import MethodType
from typing import Any

from fastapi.responses import JSONResponse
from httpx import AsyncClient
from httpx import Response as HttpxResponse
from pandas import DataFrame, read_csv

from src.adapters.presenters.error_response import ErrorResponse
from src.core.common.types import Articles, Json
from src.core.config.config import TOKEN
from src.framework.fastapi.main import app
from tests.helpers.models import Request, Response


async def app_request(url: str, headers: dict | None = None) -> HttpxResponse:
    headers = headers if headers else {TOKEN_HEADER: TOKEN}
    async with AsyncClient(app=app) as client:
        response = await client.get(url, headers=headers, timeout=15)
    return response


def path(target: MethodType):
    return f"{target.__module__}.{target.__qualname__}"


def exception_response(response: JSONResponse) -> ErrorResponse:
    data: Json = loads(response.body.decode())  # type: ignore
    if data.get("request"):
        data["request"] = Request()
    return ErrorResponse.model_validate(data)


def content_response(response: HttpxResponse) -> DataFrame:
    buffer_data = StringIO(response.content.decode())
    return read_csv(buffer_data, sep=";", keep_default_na=False)


def entry_item(scopus_id: int) -> dict[str, str]:
    return {
        "@_fa": "true",
        "prism:url": f"https://api.elsevier.com/scopus_id/{scopus_id}",
        "dc:identifier": f"SCOPUS_ID:{scopus_id}",
    }


def abstract(
    title: str = None, doi: str = None, author: str = None
) -> dict[str, Any]:
    return {
        "abstracts-retrieval-response": {
            "coredata": {
                "dc:identifier": "SCOPUS_ID:any",
                "eid": "any",
                "dc:title": title if title else "any",
                "prism:publicationName": "any",
                "prism:volume": "any",
                "prism:coverDate": "any",
                "prism:doi": doi if doi else "any",
                "citedby-count": "any",
                "dc:creator": {
                    "author": [
                        {"ce:indexed-name": author if author else "any"}
                    ]
                },
            }
        }
    }


def pagination(entry: Articles) -> list[Response]:
    total = (len(entry) * 25) - 1
    return [Response(scopus_json(total, [article])) for article in entry]


def scopus_json(total: int, entry: Articles) -> dict:
    return {
        "search-results": {
            "opensearch:totalResults": total,
            "opensearch:itemsPerPage": 25,
            "entry": entry,
        }
    }
