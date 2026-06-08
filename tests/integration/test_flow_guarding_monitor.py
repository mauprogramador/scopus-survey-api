# mypy: disable-error-code="index"
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker
from starlette.middleware.base import _StreamingResponse

from src.adapters.presenters.csv_response import CSVResponse
from src.adapters.presenters.json_response import ErrorJSON
from src.adapters.presenters.template_response import TemplateResponse
from src.core.config.config import HEADERS, RATELIMIT_POLICY, SERVER
from src.core.data.enums import ExcMsg
from src.framework.fastapi.csrf_token import CSRFToken
from src.framework.fastapi.routes import favicon
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


RETRIEVE = Patch(CSVResponse.retrieve).classmethod(favicon)
GENERATE = Patch(CSRFToken.generate_csrf_tokens).classmethod(favicon)


@mark.asyncio
async def test_success_headers(client: Client):
    client.cookies.clear()
    client.headers.clear()
    res = await client.get(URL_WEB)
    assert res.status_code == HTTP_200
    assert res.headers["X-Trace-ID"] and res.headers["X-Process-Time"]
    assert res.headers["Content-Security-Policy"] is not None
    headers = {key.lower(): value for key, value in HEADERS.items()}
    assert headers.items() <= dict(res.headers).items()
    assert res.headers["X-RateLimit-Policy"] == RATELIMIT_POLICY
    assert res.headers["Server"] == SERVER.get()


@mark.asyncio
async def test_uncaught_exception(mocker: Mocker, client: Client):
    mocker.patch(**RETRIEVE(RuntimeError("any")))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_500, ExcMsg.UNEXPECTED_ERROR)
    assert details[0]["type"] == fqn(RuntimeError)
    assert details[0]["message"] == "any"


@mark.asyncio
async def test_routing_error(mocker: Mocker, client: Client):
    client.cookies.clear()
    client.headers.clear()
    spy = mocker.spy(TemplateResponse, "not_found_template")
    res = await client.get("/api/any")
    assert res.status_code == HTTP_404 and res.text
    assert res.headers["Content-Type"] == HTML_CONTENT_TYPE
    isinstance(spy.call_args_list[0].args[1], _StreamingResponse)


@mark.asyncio
async def test_internal_error(mocker: Mocker, client: Client):
    client.cookies.clear()
    client.headers.clear()
    mocker.patch(**GENERATE(RuntimeError("any")))
    spy = mocker.spy(TemplateResponse, "not_found_template")
    res = await client.get(URL_WEB)
    assert res.status_code == HTTP_500 and res.text
    assert res.headers["Content-Type"] == HTML_CONTENT_TYPE
    isinstance(spy.call_args_list[0].args[1], ErrorJSON)
