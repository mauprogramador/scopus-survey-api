# mypy: disable-error-code="index"
import json

import anyio
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import _StreamingResponse

from src.adapters.presenters.csv_response import retrieve_csv
from src.adapters.presenters.jinja_response import get_not_found_template
from src.adapters.presenters.json_response import ErrorJSON
from src.core.common.types import Json
from src.core.config.config import HEADERS, RATELIMIT_POLICY, SERVER
from src.core.data.enums import ExcMsg
from src.framework.fastapi.csrf_token import generate_csrf_token
from src.framework.fastapi.routes import favicon
from src.framework.middleware.flow_guarding_monitor import (
    FlowGuardingMonitorMiddleware,
)
from tests.conftest import assert_error_json
from tests.mocks.helpers import Patch, fqn
from tests.mocks.raw import (
    CSV_PARAMS,
    HTML_CONTENT_TYPE,
    HTTP_200,
    HTTP_404,
    HTTP_500,
    URL_CSV,
    URL_WEB,
)


RETRIEVE = Patch(favicon, retrieve_csv)
GENERATE = Patch(favicon, generate_csrf_token)
NOT_FOUND = fqn(FlowGuardingMonitorMiddleware, get_not_found_template)


@mark.asyncio
async def test_success_headers(client: Client):
    client.cookies.clear()
    client.headers.clear()
    res = await client.get(URL_WEB)
    assert res.status_code == HTTP_200
    assert res.headers["X-Trace-ID"] and res.headers["X-Process-Time"]
    assert float(res.headers["X-Process-Time"]) >= 0
    assert res.headers["Content-Security-Policy"] is not None
    headers = {key.lower(): value for key, value in HEADERS.items()}
    assert headers.items() <= dict(res.headers).items()
    assert res.headers["X-RateLimit-Policy"] == RATELIMIT_POLICY
    assert res.headers["Server"] == SERVER.get()


@mark.asyncio
async def test_uncaught_exception(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(RuntimeError("any")))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_500, ExcMsg.INTERNAL_ERROR)
    assert details[0]["type"] == fqn(RuntimeError)
    assert details[0]["message"] == "any"
    assert details[0]["cause"]["type"] == fqn(anyio.EndOfStream)


@mark.asyncio
async def test_routing_error(mocker: Mocker, client: Client):
    client.cookies.clear()
    client.headers.clear()
    spy = mocker.patch(NOT_FOUND, wraps=get_not_found_template)
    res = await client.get("/api/any")
    assert res.status_code == HTTP_404 and res.text
    assert res.headers["Content-Type"] == HTML_CONTENT_TYPE
    spy_res = spy.call_args_list[0].args[1]
    assert isinstance(spy_res, _StreamingResponse)
    raw: Json = json.loads(spy_res.body.decode())  # type: ignore
    assert raw["details"][0]["type"] == fqn(StarletteHTTPException)
    assert raw["details"][0]["message"] == "Not Found"


@mark.asyncio
async def test_internal_error(mocker: Mocker, client: Client):
    client.cookies.clear()
    client.headers.clear()
    mocker.patch(**GENERATE(RuntimeError("any")))
    spy = mocker.patch(NOT_FOUND, wraps=get_not_found_template)
    res = await client.get(URL_WEB)
    assert res.status_code == HTTP_500 and res.text
    assert res.headers["Content-Type"] == HTML_CONTENT_TYPE

    spy_res = spy.call_args_list[0].args[1]
    assert isinstance(spy_res, ErrorJSON)
    raw: Json = json.loads(spy_res.body.decode())  # type: ignore
    assert raw["details"][0]["type"] == fqn(RuntimeError)
    assert raw["details"][0]["message"] == "any"
    assert raw["details"][0]["cause"]["type"] == fqn(anyio.EndOfStream)
