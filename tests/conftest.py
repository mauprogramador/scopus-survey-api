import asyncio
import json
import logging
from http import HTTPStatus
from unittest.mock import AsyncMock
from urllib.parse import urljoin

import aiolimiter
import httpx
import uvloop
from pytest import ExceptionInfo, LogCaptureFixture, MonkeyPatch, fixture
from pytest_asyncio import fixture as async_fixture
from pytest_mock import MockerFixture as Mocker

from src.adapters.exceptions import BaseHTTPError
from src.adapters.persistence import csv_builder as csv_builder_module
from src.adapters.presenters import csv_response as csv_response_module
from src.adapters.presenters.jinja_response import build_all_templates
from src.adapters.presenters.json_response import ErrorJSON, ErrorResponse
from src.core.domain.types import Json
from src.infra.config.config import PREFIX, SERVER
from src.infra.fastapi.main import app
from src.infra.http.http_client import HTTPClient
from src.infra.i18n.translations import load_translations
from src.infra.utils.logger import TEST_FORMATTER
from tests.mocks.helpers import MockAsyncContext, fqn
from tests.mocks.raw import (
    CSRF_TOKEN,
    CSV_FILE_NAME,
    DIRECTORY,
    SIGNED_TOKEN,
    TEMP_DIR,
)


uvloop.install()

BASE_URL = urljoin("http://127.0.0.1:123", PREFIX)
TRANSPORT = httpx.ASGITransport(app=app, client=("127.0.0.1", 123))

SLEEP = fqn(HTTPClient, asyncio.sleep, "asyncio")
LIMITER = fqn(HTTPClient, aiolimiter.AsyncLimiter, "aiolimiter")
SEMAPHORE = fqn(HTTPClient, asyncio.Semaphore, "asyncio")


@fixture(scope="session")
def session_data():
    data = {"code": "None"}
    yield data


@fixture(scope="session")
def event_loop_policy():
    return uvloop.EventLoopPolicy()


@fixture(autouse=True, scope="function")
def apply_custom_logging_formatter_to_pytest(caplog: LogCaptureFixture):
    caplog.handler.setFormatter(TEST_FORMATTER)
    # LogCaptureHandler of caplog and report handlers
    logging.getLogger().handlers[-1].setFormatter(TEST_FORMATTER)
    logging.getLogger().handlers[-2].setFormatter(TEST_FORMATTER)
    yield


@fixture(scope="session", autouse=True)
def lifespan():
    SERVER.set("Pytest/1.2.3")
    setattr(app.state.limiter, "enabled", False)

    build_all_templates(*load_translations())
    csv_file_path = DIRECTORY / CSV_FILE_NAME

    csv_file_path.write_text("any")
    print("\033[93mSession Started\033[m")

    with MonkeyPatch.context() as mp:
        mp.setattr(f"{csv_builder_module.__name__}.DIRECTORY", DIRECTORY)
        mp.setattr(f"{csv_response_module.__name__}.DIRECTORY", DIRECTORY)

        yield

    csv_file_path.unlink(missing_ok=True)
    TEMP_DIR.cleanup()
    print("\033[93mSession Ended\033[m")


@async_fixture(name="client")
async def httpx_async_client(mocker: Mocker):
    """HTTPX Async Client with ASGITransport fixture"""

    mocker.patch(LIMITER, new_callable=MockAsyncContext)
    mocker.patch(SEMAPHORE, new_callable=MockAsyncContext)
    mock_sleep = mocker.patch(SLEEP, new_callable=AsyncMock)

    async with httpx.AsyncClient(
        cookies={"csrf-token": SIGNED_TOKEN},
        headers={"X-CSRF-Token": CSRF_TOKEN},
        timeout=15,
        base_url=BASE_URL,
        transport=TRANSPORT,
    ) as client:
        setattr(client, "mock_sleep", mock_sleep)
        yield client


def assert_http_error(
    info: ExceptionInfo[BaseHTTPError],
    code: HTTPStatus,
    message: str,
) -> list[Json] | None:
    """Asserts HTTPError data"""
    assert info.value.status_code == code
    assert info.value.message == message
    return info.value.details


def assert_error_json(
    res: ErrorJSON | httpx.Response,
    code: HTTPStatus,
    message: str,
) -> list[Json] | None:
    """Asserts ErrorJson and HTTPX Response data"""
    if isinstance(res, ErrorJSON):
        data: Json = json.loads(res.body.decode())  # type: ignore
    else:
        data: Json = res.json()

    error_res = ErrorResponse.model_validate(data)

    assert not error_res.success and error_res.timestamp and error_res.request
    assert error_res.status_code == code.value
    assert error_res.status == code.phrase
    assert error_res.message == message

    return error_res.details
