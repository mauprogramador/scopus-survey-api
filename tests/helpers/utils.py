from io import StringIO
from json import loads
from types import MethodType

from fastapi.responses import JSONResponse
from httpx import AsyncClient, Response as HttpxResponse
from pandas import DataFrame, read_csv

from app.core.config.config import TOKEN, TOKEN_HEADER
from app.framework.exceptions.http_exceptions import BaseExceptionResponse
from app.framework.fastapi.main import app
from tests.helpers.models import Response


async def app_request(url: str, headers: dict | None = None) -> HttpxResponse:
    headers = headers if headers else {TOKEN_HEADER: TOKEN}
    async with AsyncClient(app=app) as client:
        response = await client.get(url, headers=headers, timeout=15)
    return response


def path(target: MethodType):
    return f"{target.__module__}.{target.__qualname__}"


def exception_response(response: JSONResponse) -> BaseExceptionResponse:
    return BaseExceptionResponse.model_validate(loads(response.body.decode()))


def content_response(response: HttpxResponse) -> DataFrame:
    buffer_data = StringIO(response.content.decode())
    return read_csv(buffer_data, sep=";", keep_default_na=False)


def request_mock(
    pages: list[Response], value: str | Response | list
) -> list[Response]:
    if isinstance(value, str):
        responses = len(pages) * [Response(value)]
    else:
        responses = len(pages) * [value]
    return [*pages, *responses]
