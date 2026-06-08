import json
import logging
from http import HTTPStatus
from urllib.parse import urljoin

import httpx
import uvloop
from pytest import ExceptionInfo, LogCaptureFixture, fixture
from pytest_asyncio import fixture as async_fixture

from src.adapters.presenters.json_response import ErrorJSON, ErrorResponse
from src.adapters.presenters.template_response import TemplateResponse
from src.core.common.types import Json
from src.core.config.config import DIRECTORY, PREFIX, SERVER
from src.core.domain.http_exceptions import HTTPError
from src.core.domain.translations import load_translations
from src.framework.fastapi.main import app
from src.utils.logger import TEST_FORMATTER
from tests.mocks.raw import CSRF_TOKEN, CSV_FILE_NAME, SIGNED_TOKEN


uvloop.install()
TIMEOUT = 15
BASE_URL = urljoin("http://127.0.0.1:123", PREFIX)
TRANSPORT = httpx.ASGITransport(app=app, client=("127.0.0.1", 123))


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

    translations = load_translations()
    TemplateResponse.build_all(*translations)
    csv_file_path = DIRECTORY / CSV_FILE_NAME

    DIRECTORY.mkdir(parents=True, exist_ok=True)
    csv_file_path.write_text("any")

    print("\033[93mPytest Session Start\033[m", flush=True)

    yield

    csv_file_path.unlink(missing_ok=True)
    print("\033[93mPytest Session Finish\033[m", flush=True)


@async_fixture(name="client")
async def httpx_async_client():
    """HTTPX Async Client with ASGITransport fixture"""
    async with httpx.AsyncClient(
        cookies={"csrf-token": SIGNED_TOKEN},
        headers={"X-CSRF-Token": CSRF_TOKEN},
        timeout=TIMEOUT,
        base_url=BASE_URL,
        transport=TRANSPORT,
    ) as client:
        yield client


def assert_http_error(
    info: ExceptionInfo[HTTPError],
    code: HTTPStatus,
    message: str,
) -> None:
    """Asserts HTTPError data"""
    assert info.value.status == info.value.status_code == code
    assert info.value.message == info.value.detail == message


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
