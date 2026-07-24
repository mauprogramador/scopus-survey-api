import secrets

from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.domain.enums import Lang
from tests.mocks.helpers import get_patch
from tests.mocks.integration import COMBINATION_RESPONSES, SURVEY_RESPONSES
from tests.mocks.raw import (
    COMBINATION_PARAMS,
    CSV_PARAMS,
    HTTP_200,
    HTTP_404,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_CSV,
    URL_SEARCH,
    URL_WEB,
)


@mark.asyncio
async def test_favicon(client: Client):
    client.base_url = "http://127.0.0.1:123"
    res = await client.get("/favicon.ico")
    assert res.status_code == HTTP_200
    assert res.headers["Cache-Control"]
    assert "favicon.ico" in res.headers["Content-Disposition"]
    assert res.headers["Content-Type"] == "image/x-icon"


@mark.asyncio
async def test_web_search_articles_en_us(client: Client):
    client.cookies.clear()
    client.headers.clear()
    res = await client.get(URL_WEB)
    assert res.status_code == HTTP_200 and res.text
    assert res.cookies["csrf-token"] is not None
    assert "text/html" in res.headers["Content-Type"]


@mark.asyncio
async def test_web_search_articles_pt_br(client: Client):
    client.cookies.clear()
    client.headers.clear()
    res = await client.get(f"/web/{Lang.PT_BR}/survey-bibliographies")
    assert res.status_code == HTTP_200 and res.text
    assert res.cookies["csrf-token"] is not None
    assert "text/html" in res.headers["Content-Type"]


@mark.asyncio
async def test_api_combination(mocker: Mocker, client: Client):
    mocker.patch(*get_patch(COMBINATION_RESPONSES))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and res.text
    assert "application/json" in res.headers["Content-Type"]


@mark.asyncio
async def test_api_survey(mocker: Mocker, client: Client):
    mocker.patch(*get_patch(SURVEY_RESPONSES))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and res.text
    assert "text/csv" in res.headers["Content-Type"]


@mark.asyncio
async def test_api_csv_success(client: Client):
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.status_code == HTTP_200 and res.text
    assert "text/csv" in res.headers["Content-Type"]


@mark.asyncio
async def test_api_csv_not_found(mocker: Mocker, client: Client):
    mocker.patch.dict(CSV_PARAMS, {"apiKey": secrets.token_hex(16)})
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.status_code == HTTP_404
    assert "application/json" in res.headers["Content-Type"]
