# mypy: disable-error-code="index"
from httpx import AsyncClient as Client
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic_core import ValidationError
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.domain.enums import ExcMsg
from src.infra.config.config import MAX_AGE
from tests.conftest import assert_error_json
from tests.mocks.helpers import fqn
from tests.mocks.raw import (
    CSV_PARAMS,
    HTTP_200,
    HTTP_401,
    SIGNED_TOKEN,
    URL_CSV,
    URL_WEB,
)


@mark.asyncio
async def test_set_cookie(client: Client):
    client.cookies.delete("csrf-token")
    res = await client.get(URL_WEB)
    assert res.headers.get("set-cookie") is not None
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_missing_cookie_token(client: Client):
    client.cookies.delete("csrf-token")
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_401, ExcMsg.TOKEN_COOKIE_ERROR)
    assert details is None


@mark.asyncio
async def test_missing_header_token(client: Client):
    client.headers.clear()
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_401, ExcMsg.TOKEN_HEADER_ERROR)
    assert details is None


@mark.asyncio
async def test_invalid_token(client: Client):
    client.headers.update({"X-CSRF-Token": "any"})
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_401, ExcMsg.INVALID_TOKEN)
    assert details[0]["type"] == fqn(ValidationError)
    assert details[0]["message"]
    assert details[0]["errors"][0]["type"] == "string_too_short"


@mark.asyncio
async def test_signature_expired(mocker: Mocker, client: Client):
    mock = mocker.patch.object(
        URLSafeTimedSerializer,
        "loads",
        side_effect=SignatureExpired("any"),
    )
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    mock.assert_called_once_with(SIGNED_TOKEN, MAX_AGE)
    details = assert_error_json(res, HTTP_401, ExcMsg.EXPIRED_TOKEN)
    assert details[0]["type"] == fqn(SignatureExpired)
    assert details[0]["message"] == "any"
    assert details[0]["signature"]["payload"] is None
    assert details[0]["signature"]["date_signed"] is None


@mark.asyncio
async def test_bad_signature(client: Client):
    client.cookies.update({"csrf-token": "any"})
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    details = assert_error_json(res, HTTP_401, ExcMsg.TOKEN_SIGNATURE_ERROR)
    assert details[0]["type"] == fqn(BadSignature)
    assert details[0]["message"]
    assert details[0]["signature"]["payload"] is None


@mark.asyncio
async def test_incorrect(mocker: Mocker, client: Client):
    mock = mocker.patch.object(
        URLSafeTimedSerializer, "loads", return_value="any"
    )
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    mock.assert_called_once_with(SIGNED_TOKEN, MAX_AGE)
    details = assert_error_json(res, HTTP_401, ExcMsg.INVALID_TOKEN)
    assert details is None
