import pytest

from app.core.common.messages import INVALID_ACCESS_TOKEN, MISSING_ACCESS_TOKEN
from app.core.config.config import TOKEN
from app.framework.exceptions import Unauthorized
from tests.helpers.models import Request
from tests.mocks.common import API_KEY
from tests.mocks.fixtures import ACCESS_TOKEN


@pytest.mark.asyncio
async def test_request_token():
    assert await ACCESS_TOKEN(Request(TOKEN), None) is None


@pytest.mark.asyncio
async def test_missing_request_token():
    with pytest.raises(Unauthorized) as error:
        await ACCESS_TOKEN(Request(), None)
    assert error.value.status_code == 401
    assert error.value.message == MISSING_ACCESS_TOKEN


@pytest.mark.asyncio
async def test_invalid_request_token():
    with pytest.raises(Unauthorized) as error:
        await ACCESS_TOKEN(Request("any"), None)
    assert error.value.status_code == 401
    assert error.value.message == INVALID_ACCESS_TOKEN


@pytest.mark.asyncio
async def test_different_request_token():
    with pytest.raises(Unauthorized) as error:
        await ACCESS_TOKEN(Request(API_KEY), None)
    assert error.value.status_code == 401
    assert error.value.message == INVALID_ACCESS_TOKEN


@pytest.mark.asyncio
async def test_header_token():
    assert await ACCESS_TOKEN(Request(), TOKEN) is None


@pytest.mark.asyncio
async def test_invalid_header_token():
    with pytest.raises(Unauthorized) as error:
        await ACCESS_TOKEN(Request(), "any")
    assert error.value.status_code == 401
    assert error.value.message == INVALID_ACCESS_TOKEN


@pytest.mark.asyncio
async def test_different_header_token():
    with pytest.raises(Unauthorized) as error:
        await ACCESS_TOKEN(Request(), API_KEY)
    assert error.value.status_code == 401
    assert error.value.message == INVALID_ACCESS_TOKEN
