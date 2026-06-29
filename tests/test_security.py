# mypy: disable-error-code="index"
import asyncio
from http import HTTPStatus
from typing import cast
from unittest.mock import AsyncMock

from httpx import AsyncClient as Client
from itsdangerous import SignatureExpired
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.config.config import DIRECTORY, PREFIX
from src.core.data.enums import ExcMsg
from src.framework.fastapi import csrf_token as csrf_token_module
from src.framework.fastapi import routes as routes_module
from tests.conftest import SLEEP, assert_error_json
from tests.mocks.errors import STARLETTE_HTTP_EXCEPTION
from tests.mocks.helpers import fqn, trans
from tests.mocks.raw import (
    CSRF_TOKEN,
    CSV_FILE_NAME,
    CSV_PARAMS,
    HTTP_200,
    HTTP_401,
    SIGNED_TOKEN,
    URL_CSV,
    URL_WEB,
)


@mark.asyncio
async def test_cors_headers(client: Client):
    # NOTE: Configure CORS origins and allowed headers for prod
    origin = "https://somedomain.com"
    headers = {"Origin": origin, "X-Any-Header": "any"}
    res = await client.get(URL_CSV, params=CSV_PARAMS, headers=headers)
    assert res.status_code == HTTP_200
    assert res.headers.get("access-control-allow-origin") == origin
    assert res.headers.get("Access-Control-Allow-Credentials") is None


@mark.asyncio
async def test_cors_invalid_method(client: Client):
    code = HTTPStatus.METHOD_NOT_ALLOWED
    res = await client.post(URL_CSV)
    details = assert_error_json(res, code, trans(STARLETTE_HTTP_EXCEPTION))
    assert details[0]["message"] == code.phrase


@mark.asyncio
async def test_https_scheme(client: Client):
    client.cookies.clear()
    client.headers.clear()
    res = await client.get(f"https://127.0.0.1:123{PREFIX}{URL_WEB}")
    assert res.status_code == HTTP_200


@mark.parametrize(
    "dast_input",
    [
        "<script>alert('compromised')</script>",
        "<img src=x onerror=alert(1)>",
        "../../../../etc/passwd",
        "..\\..\\..\\windows\\win.ini",
    ],
    ids=["XSS-1", "XSS-2", "Path-1", "Path-2"],
)
@mark.asyncio
async def test_dast_extra_input_injection(dast_input: str, client: Client):
    # NOTE: Ignore, strip or raise errors for extra inputs in prod
    client.cookies.clear()
    client.headers.clear()
    res = await client.get(
        URL_WEB,
        params={"any": dast_input},
        cookies={"any": dast_input},
        auth=("any", dast_input),
    )
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_security_headers(client: Client):
    # TODO: implement tests with Playwright
    client.cookies.clear()
    client.headers.clear()
    res = await client.get(URL_WEB)
    assert res.status_code == HTTP_200
    assert res.headers["Content-Security-Policy"] is not None
    assert res.headers["Cross-Origin-Opener-Policy"] is not None
    assert res.headers["Referrer-Policy"] is not None
    assert res.headers["X-Content-Type-Options"] is not None
    assert res.headers["X-Frame-Options"] is not None
    assert res.headers["X-XSS-Protection"] is not None


@mark.asyncio
async def test_double_submit_csrf_flow(client: Client):
    assert (DIRECTORY / CSV_FILE_NAME).exists()
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.status_code == HTTP_200

    client.cookies.clear()
    client.headers.clear()

    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.status_code == HTTP_401

    res = await client.get(URL_WEB)
    assert res.headers.get("set-cookie") is not None
    assert res.status_code == HTTP_200

    signed_token = res.cookies.get("csrf-token")
    csrf_token = res.headers.get("X-CSRF-Token")
    assert signed_token and csrf_token

    # Previous generate still not expired
    res = await client.get(
        URL_CSV,
        params=CSV_PARAMS,
        cookies={"csrf-token": SIGNED_TOKEN},
        headers={"X-CSRF-Token": CSRF_TOKEN},
    )
    assert res.status_code == HTTP_200

    res = await client.get(
        URL_CSV,
        params=CSV_PARAMS,
        cookies={"csrf-token": signed_token},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert res.status_code == HTTP_200
    assert "csrf-token" in client.cookies


@mark.asyncio
async def test_csrf_token_expiry_and_refresh(mocker: Mocker, client: Client):
    mock_sleep = cast(AsyncMock, getattr(client, "mock_sleep"))
    client.cookies.clear()
    client.headers.clear()

    mocker.patch(f"{routes_module.__name__}.MAX_AGE", 1)

    res = await client.get(URL_WEB)
    assert "Max-Age=1" in res.headers["set-cookie"]
    assert res.status_code == HTTP_200

    signed_token = res.cookies.get("csrf-token")
    assert signed_token is not None

    csrf_token = res.headers.get("X-CSRF-Token")
    assert csrf_token is not None

    mocker.stop(mock_sleep)
    await asyncio.sleep(2)

    mocker.patch(SLEEP, new_callable=AsyncMock)
    mocker.patch(f"{csrf_token_module.__name__}.MAX_AGE", 1)

    res = await client.get(
        URL_CSV,
        params=CSV_PARAMS,
        cookies={"csrf-token": signed_token},
        headers={"X-CSRF-Token": csrf_token},
    )
    details = assert_error_json(res, HTTP_401, ExcMsg.EXPIRED_TOKEN)
    assert details[0]["type"] == fqn(SignatureExpired)
    assert "2 > 1" in details[0]["message"]

    mocker.stopall()

    res = await client.get(URL_WEB)
    assert "Max-Age=3600" in res.headers["set-cookie"]
    assert res.status_code == HTTP_200

    assert signed_token != res.cookies.get("csrf-token")
    assert csrf_token != res.headers.get("X-CSRF-Token")
