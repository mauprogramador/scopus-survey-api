# mypy: disable-error-code="index"
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker
from starlette.middleware.base import _StreamingResponse

from src.adapters.presenters.csv_response import CSVResponse
from src.adapters.presenters.json_response import ErrorJSON
from src.adapters.presenters.template_response import TemplateResponse
from tests.conftest import assert_error_json
from tests.mocks.helpers import fqn
from tests.mocks.raw import (
    CSV_PARAMS,
    HTML_CONTENT_TYPE,
    HTTP_200,
    HTTP_404,
    HTTP_500,
    URL_CSV,
    URL_WEB,
)

RETRIEVE = fqn(CSVResponse.retrieve)


@mark.asyncio
async def test_success_process_time(client: Client):
    client.cookies.clear()
    client.headers.clear()
    res = await client.get(URL_WEB)
    assert res.status_code == HTTP_200
    assert res.headers["X-Process-Time"] and res.headers["X-RateLimit-Policy"]


@mark.asyncio
async def test_uncaught_exception(mocker: Mocker, client: Client):
    mocker.patch(RETRIEVE, side_effect=RuntimeError("any"))
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    errors = assert_error_json(res, HTTP_500, "any")
    assert errors[0]["type"] == fqn(RuntimeError)
    assert errors[0]["detail"] == "any"


@mark.asyncio
async def test_not_found_status(mocker: Mocker, client: Client):
    client.cookies.clear()
    client.headers.clear()
    spy = mocker.spy(TemplateResponse, "not_found_template")
    res = await client.get("/api/any")
    assert res.status_code == HTTP_404 and res.text
    assert res.headers["Content-Type"] == HTML_CONTENT_TYPE
    isinstance(spy.call_args_list[0].args[1], _StreamingResponse)


@mark.asyncio
async def test_not_found_error(mocker: Mocker, client: Client):
    client.cookies.clear()
    client.headers.clear()
    spy = mocker.spy(TemplateResponse, "not_found_template")
    res = await client.get("/api/any")
    assert res.status_code == HTTP_404 and res.text
    assert res.headers["Content-Type"] == HTML_CONTENT_TYPE
    isinstance(spy.call_args_list[0].args[1], ErrorJSON)
