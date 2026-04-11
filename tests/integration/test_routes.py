from secrets import token_hex
from unittest.mock import AsyncMock

from aiohttp_retry import RetryClient
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.data.enums import Lang
from tests.mocks.helpers import fqn
from tests.mocks.integration import COMBINATION_RESPONSES, SURVEY_RESPONSES
from tests.mocks.raw import (
    COMBINATION_PARAMS,
    CSV_CONTENT_TYPE,
    CSV_PARAMS,
    HTML_CONTENT_TYPE,
    HTTP_200,
    HTTP_404,
    JSON_CONTENT_TYPE,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_CSV,
    URL_SEARCH,
    URL_WEB,
)

GET = fqn(RetryClient.get)


@mark.asyncio
async def test_favicon(client: Client):
    client.base_url = "http://127.0.0.1:123"
    res = await client.get("/favicon.ico")
    assert res.status_code == HTTP_200
    assert res.headers["Cache-Control"]
    assert res.headers["Content-Disposition"].count("favicon.ico")
    assert res.headers["Content-Type"] == "image/x-icon"


@mark.asyncio
async def test_web_search_articles_en_us(client: Client):
    client.cookies.clear()
    client.headers.clear()
    res = await client.get(URL_WEB)
    assert res.status_code == HTTP_200 and res.text
    assert res.cookies.get("session") is not None
    assert res.cookies.get("csrf-token") is not None
    assert res.headers.get("Content-Type") == HTML_CONTENT_TYPE


@mark.asyncio
async def test_web_search_articles_pt_br(client: Client):
    client.cookies.clear()
    client.headers.clear()
    res = await client.get(f"/web/{Lang.PT_BR}/survey-bibliographies")
    assert res.status_code == HTTP_200 and res.text
    assert res.cookies.get("session") is not None
    assert res.cookies.get("csrf-token") is not None
    assert res.headers.get("Content-Type") == HTML_CONTENT_TYPE


@mark.asyncio
async def test_api_combination(mocker: Mocker, client: Client):
    mocker.patch(GET, new=AsyncMock(side_effect=COMBINATION_RESPONSES))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and res.text
    assert res.cookies.get("session") is not None
    assert res.headers.get("Content-Type") == JSON_CONTENT_TYPE


@mark.asyncio
async def test_api_survey(mocker: Mocker, client: Client):
    mocker.patch(GET, new=AsyncMock(side_effect=SURVEY_RESPONSES))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and res.text
    assert res.cookies.get("session") is not None
    assert res.headers.get("Content-Type") == CSV_CONTENT_TYPE


@mark.asyncio
async def test_api_csv_success(client: Client):
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.status_code == HTTP_200 and res.text
    assert res.cookies.get("session") is not None
    assert res.headers.get("Content-Type") == CSV_CONTENT_TYPE


@mark.asyncio
async def test_api_csv_not_found(client: Client):
    CSV_PARAMS.update({"apiKey": token_hex(16)})
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.status_code == HTTP_404
    assert res.cookies.get("session") is not None
    assert res.headers.get("Content-Type") in JSON_CONTENT_TYPE
