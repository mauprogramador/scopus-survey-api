from http import HTTPStatus
from json import loads
from urllib.parse import urljoin

from httpx import ASGITransport, AsyncClient, Response
from pytest import ExceptionInfo, fixture
from pytest_asyncio import fixture as async_fixture
from uvloop import EventLoopPolicy, install

from src.adapters.presenters.json_response import ErrorJSON, ErrorResponse
from src.core.common.types import Json
from src.core.config.config import DIRECTORY, PREFIX, SERVER
from src.core.domain.http_exceptions import HTTPError
from src.core.domain.translations import Translations
from src.framework.fastapi.main import app
from tests.mocks.raw import CSRF_TOKEN, CSV_FILE_NAME, SIGNED_TOKEN, URL_WEB

install()
TIMEOUT = 15
BASE_URL = urljoin("http://127.0.0.1:123", PREFIX)
TRANSPORT = ASGITransport(app=app, client=("127.0.0.1", 123))


@fixture(scope="session")
def session_data():
    data = {"code": "None"}
    yield data


@fixture(scope="session")
def event_loop_policy():
    return EventLoopPolicy()


@fixture(scope="session", autouse=True)
def lifespan():
    SERVER.set("Pytest/1.2.3")

    Translations.load_all()
    csv_file_path = DIRECTORY / CSV_FILE_NAME

    DIRECTORY.mkdir(parents=True, exist_ok=True)
    csv_file_path.write_text("any")

    print("\033[93mPytest Session Start\033[m", flush=True)

    yield

    csv_file_path.unlink(missing_ok=True)
    print("\033[93mPytest Session Finish\033[m", flush=True)


@async_fixture(scope="session", loop_scope="session", name="session_cookie")
async def load_starlette_session_cookie():
    async with AsyncClient(
        timeout=TIMEOUT, base_url=BASE_URL, transport=TRANSPORT
    ) as client:
        response = await client.get(URL_WEB)
        assert response.status_code == HTTPStatus.OK
        assert "session" in client.cookies

        yield client.cookies.get("session")


@async_fixture(name="client")
async def httpx_async_client(session_cookie: str):
    """HTTPX Async Client with ASGITransport fixture"""
    async with AsyncClient(
        cookies={"session": session_cookie, "csrf-token": SIGNED_TOKEN},
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
    response: ErrorJSON | Response,
    code: HTTPStatus,
    message: str,
) -> list[Json] | None:
    """Asserts ErrorJson and HTTPX Response data"""
    if isinstance(response, ErrorJSON):
        data: Json = loads(response.body.decode())  # type: ignore
    else:
        data: Json = response.json()

    error_res = ErrorResponse.model_validate(data)

    assert not error_res.success and error_res.timestamp and error_res.request
    assert error_res.status_code == code.value
    assert error_res.status == code.phrase
    assert error_res.message == message

    return error_res.errors
