from pathlib import Path
from random import randint
from secrets import token_hex
from unittest.mock import AsyncMock

from aiohttp_retry import RetryClient
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker
from thefuzz.fuzz import partial_ratio

from src.adapters.helpers.url_builder import URLBuilder
from src.core.common.error_messages import CSV_NOT_FOUND
from src.core.config.config import DIRECTORY, FILE
from src.core.config.scopus import DATA_SOURCE_NOTE
from src.core.data.enums import Column
from tests.conftest import assert_error_json
from tests.mocks.helpers import (
    fqn,
    load_csv_file_response_dataframe,
    response_mock,
    search_raw,
)
from tests.mocks.raw import (
    CSV_CONTENT_TYPE,
    HTML_CONTENT_TYPE,
    HTTP_200,
    HTTP_404,
    JSON_CONTENT_TYPE,
    RAW_ABSTRACT_OK,
    RAW_SEARCH_OK,
    RESET_DATETIME,
    URL_COMBINATION,
    URL_CSV,
    URL_SEARCH,
    URL_WEB,
)

GET = fqn(RetryClient.get)


class TestUserFlowSurveySteps:
    """Complete user survey steps flow"""

    _token_header: str = None
    _token_session: str = None
    _token_cookie: str = None
    _api_key: str = None
    _combination: str = None
    _file_path: Path = None

    @classmethod
    def _cookies_and_headers(cls):
        cookies = {
            "session": cls._token_session,
            "csrf-token": cls._token_cookie,
        }
        headers = {"X-CSRF-Token": cls._token_header}
        return cookies, headers

    @mark.asyncio
    @classmethod
    async def test_01_web_form_spa(cls, client: Client):
        client.cookies.clear()
        client.headers.clear()

        res = await client.get(URL_WEB)
        assert res.status_code == HTTP_200
        assert res.headers.get("Content-Type") == HTML_CONTENT_TYPE

        cls._token_header = res.headers.get("X-CSRF-Token")
        cls._token_session = res.cookies.get("session")
        cls._token_cookie = res.cookies.get("csrf-token")

        assert cls._token_header is not None
        assert cls._token_session is not None
        assert cls._token_cookie is not None

    @mark.asyncio
    @classmethod
    async def test_02_previous_survey_csv(cls, client: Client):
        cls._api_key = token_hex(16)
        csv_params = {
            "csrfToken": cls._token_header,
            "apiKey": cls._api_key,
            "button": "previous",
        }
        cookies, headers = cls._cookies_and_headers()

        res = await client.get(
            URL_CSV,
            params=csv_params,
            headers=headers,
            cookies=cookies,
        )
        assert res.status_code == HTTP_404
        assert res.headers.get("Content-Type") in JSON_CONTENT_TYPE
        assert res.cookies.get("session") is not None
        assert_error_json(res, HTTP_404, CSV_NOT_FOUND)

    @mark.asyncio
    @classmethod
    async def test_03_keyword_combination(cls, mocker: Mocker, client: Client):
        combination_params = {
            "csrfToken": cls._token_header,
            "apiKey": cls._api_key,
            "keywords": ["FastAPI", "API"],
            "button": "combination",
        }
        cookies, headers = cls._cookies_and_headers()

        mocks = [response_mock(search_raw(randint(16, 256)))] * 3
        mocker.patch(GET, new=AsyncMock(side_effect=mocks))

        res = await client.get(
            URL_COMBINATION,
            params=combination_params,
            headers=headers,
            cookies=cookies,
        )
        assert res.status_code == HTTP_200
        assert res.headers.get("Content-Type") == JSON_CONTENT_TYPE
        assert res.cookies.get("session") is not None
        assert res.headers.get("X-API-Key") == cls._api_key
        assert res.headers.get("X-Keywords") == "FastAPI AND API"
        assert res.headers.get("X-Search-Limit") == "20000"
        assert res.headers.get("X-Search-Remaining") == "20000"
        assert res.headers.get("X-Search-Reset") == RESET_DATETIME
        assert res.headers.get("X-Search-ELS-Status") == "OK"
        assert res.headers.get("X-Average-Found")
        assert len(res.json()["data"]["combinations"]) == 3

        cls._combination = res.json()["data"]["combinations"][0]["combination"]

    @mark.asyncio
    @classmethod
    async def test_04_final_survey(cls, mocker: Mocker, client: Client):
        search_params = {
            "csrfToken": cls._token_header,
            "apiKey": cls._api_key,
            "keywords": ["FastAPI", "API"],
            "combination": cls._combination,
            "button": "survey",
        }
        cookies, headers = cls._cookies_and_headers()

        mocks = [response_mock(RAW_SEARCH_OK), response_mock(RAW_ABSTRACT_OK)]
        mocker.patch(GET, new=AsyncMock(side_effect=mocks))

        res = await client.get(
            URL_SEARCH,
            params=search_params,
            headers=headers,
            cookies=cookies,
        )
        assert res.status_code == HTTP_200
        assert res.headers.get("Content-Type") == CSV_CONTENT_TYPE
        assert res.cookies.get("session") is not None
        assert res.headers.get("X-API-Key") == cls._api_key
        assert res.headers.get("X-Combination") == cls._combination
        assert res.headers.get("X-Total") == "1"
        assert res.headers.get("X-Items-Per-Page") == "1"
        assert res.headers.get("X-Pages-Count") == "1"
        assert res.headers.get("X-Search-Limit") == "20000"
        assert res.headers.get("X-Search-Remaining") == "20000"
        assert res.headers.get("X-Search-Reset") == RESET_DATETIME
        assert res.headers.get("X-Search-ELS-Status") == "OK"
        assert res.headers.get("X-Abstract-Limit") == "20000"
        assert res.headers.get("X-Abstract-Remaining") == "20000"
        assert res.headers.get("X-Abstract-Reset") == RESET_DATETIME
        assert res.headers.get("X-Abstract-ELS-Status") == "OK"
        assert res.headers.get("X-Loss") == "0doc / 0.00%"

        filename: str | None = res.headers.get("X-CSV-Filename")
        assert filename == f"{cls._api_key}_{cls._combination.lower()}_{FILE}"

        df = load_csv_file_response_dataframe(res)
        assert df.shape == (1, 11)
        assert df[Column.URL].iloc[0] == URLBuilder.article_page_url(
            "0123456789"
        )
        assert df[Column.AUTHORS].iloc[0] == "any_author"
        assert df[Column.TITLE].iloc[0] == "any_title"

        cls._file_path = DIRECTORY / f"{cls._api_key}_{FILE}"
        assert cls._file_path.exists()

        with cls._file_path.open(mode="r") as file:
            lines = file.readlines()
            assert len(lines) == 6

            assert lines[0].startswith("# GeneratedBy")
            assert lines[1].startswith("# Params")
            assert lines[2].startswith("# Survey")
            assert lines[3].startswith("# Source")

            assert lines[1].count(cls._api_key) == 1
            assert lines[1].count(cls._api_key) == 1
            assert lines[2].count("total=1") == 1
            assert partial_ratio(lines[3], DATA_SOURCE_NOTE) > 80

    @mark.asyncio
    @classmethod
    async def test_05_csv_download(cls, client: Client):
        csv_params = {
            "csrfToken": cls._token_header,
            "apiKey": cls._api_key,
            "button": "download",
        }
        cookies, headers = cls._cookies_and_headers()

        res = await client.get(
            URL_CSV,
            params=csv_params,
            headers=headers,
            cookies=cookies,
        )
        assert res.status_code == HTTP_200
        assert res.headers.get("Content-Type") == CSV_CONTENT_TYPE
        assert res.cookies.get("session") is not None
        assert res.headers.get("X-API-Key") == cls._api_key
        assert res.headers.get("X-CSV-Filename") is not None

        df = load_csv_file_response_dataframe(res)
        assert df.shape == (1, 11)
        assert df[Column.URL].iloc[0] == URLBuilder.article_page_url(
            "0123456789"
        )
        assert df[Column.AUTHORS].iloc[0] == "any_author"
        assert df[Column.TITLE].iloc[0] == "any_title"

        cls._file_path.unlink()
