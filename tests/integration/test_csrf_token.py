# mypy: disable-error-code="index"
from httpx import AsyncClient as Client
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic_core import ValidationError
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.common.error_messages import (
    EXPIRED_TOKEN,
    INVALID_TOKEN,
    TOKEN_COOKIE_ERROR,
    TOKEN_HEADER_ERROR,
    TOKEN_SIGNATURE_ERROR,
)
from src.core.config.config import MAX_AGE
from src.core.data.enums import Button
from tests.conftest import assert_error_json
from tests.mocks.helpers import fqn
from tests.mocks.raw import (
    API_KEY,
    CSV_PARAMS,
    HTTP_200,
    HTTP_401,
    SIGNED_TOKEN,
    URL_CSV,
)


@mark.asyncio
async def test_ok(client: Client):
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.status_code == HTTP_200
    assert res.cookies.get("session") is not None
    assert res.headers.get("set-cookie") is not None
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_missing_cookie_token(client: Client):
    client.cookies.delete("csrf-token")
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.cookies.get("session") is not None
    assert res.headers.get("set-cookie") is not None
    errors = assert_error_json(res, HTTP_401, TOKEN_COOKIE_ERROR)
    assert errors is None


@mark.asyncio
async def test_missing_header_token(client: Client):
    client.headers.clear()
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.cookies.get("session") is not None
    assert res.headers.get("set-cookie") is not None
    errors = assert_error_json(res, HTTP_401, TOKEN_HEADER_ERROR)
    assert errors is None


@mark.asyncio
async def test_missing_session_token(client: Client):
    client.cookies.delete("session")
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.cookies.get("session") is None
    assert res.headers.get("set-cookie") is None
    errors = assert_error_json(res, HTTP_401, TOKEN_SESSION_ERROR)
    assert errors is None


@mark.asyncio
async def test_signature_expired(mocker: Mocker, client: Client):
    mock = mocker.patch.object(
        URLSafeTimedSerializer,
        "loads",
        side_effect=SignatureExpired("any"),
    )
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.cookies.get("session") is not None
    assert res.headers.get("set-cookie") is not None
    mock.assert_called_once_with(SIGNED_TOKEN, MAX_AGE)
    errors = assert_error_json(res, HTTP_401, EXPIRED_TOKEN)
    assert errors[0]["type"] == fqn(SignatureExpired)
    assert errors[0]["detail"] == "any"


@mark.asyncio
async def test_bad_signature(client: Client):
    client.cookies.update({"csrf-token": "any"})
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.cookies.get("session") is not None
    assert res.headers.get("set-cookie") is not None
    errors = assert_error_json(res, HTTP_401, TOKEN_SIGNATURE_ERROR)
    assert errors[0]["type"] == fqn(BadSignature)
    assert errors[0]["detail"]


@mark.asyncio
async def test_incorrect(mocker: Mocker, client: Client):
    mock = mocker.patch.object(
        URLSafeTimedSerializer, "loads", return_value="any"
    )
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.cookies.get("session") is not None
    assert res.headers.get("set-cookie") is not None
    mock.assert_called_once_with(SIGNED_TOKEN, MAX_AGE)
    errors = assert_error_json(res, HTTP_401, INVALID_TOKEN)
    assert errors is None
