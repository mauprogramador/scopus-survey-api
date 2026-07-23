import asyncio
from unittest.mock import AsyncMock

from pydantic import ValidationError
from pytest import mark, raises

from src.adapters.helpers.fetch_multiple_concurrent import fetch_multiple
from src.core.common.types import Headers
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import HTTPError, InternalError
from tests.conftest import assert_http_error
from tests.mocks.errors import (
    TASKS_CANCELLED_ERROR,
    TASKS_COMMON_ERROR,
    TASKS_HTTP_ERROR,
)
from tests.mocks.helpers import fqn
from tests.mocks.raw import HTTP_400, RAW_HEADERS_OK


@mark.asyncio
async def test_fetch_multiple():
    async def _fetcher(index: int) -> tuple[int, Headers]:
        return index, RAW_HEADERS_OK

    results, headers = await fetch_multiple(_fetcher, range(3), range(3))
    assert len(results) == 3 and headers.status == "OK"


@mark.asyncio
async def test_fetch_multiple_task_error():
    fetcher = AsyncMock(side_effect=KeyError(0))
    with raises(KeyError) as info:
        await fetch_multiple(fetcher, range(1), range(1))
    assert isinstance(info.value, KeyError) and info.value.args[0] == 0


@mark.asyncio
async def test_fetch_multiple_no_tasks():
    with raises(InternalError) as info:
        await fetch_multiple(AsyncMock(), range(0), range(0))
    assert info.value.message == ExcMsg.INTERNAL_ERROR


@mark.asyncio
async def test_fetch_multiple_http_error():
    fetcher = AsyncMock(side_effect=TASKS_HTTP_ERROR)
    with raises(HTTPError) as info:
        await fetch_multiple(fetcher, range(6), range(6))
    assert_http_error(info, HTTP_400, ExcMsg.INTERNAL_ERROR)
    assert info.value.details[0]["type"] == fqn(ValueError)
    assert info.value.details[0]["message"] == "any"


@mark.asyncio
async def test_fetch_multiple_cancelled_error():
    fetcher = AsyncMock(side_effect=TASKS_CANCELLED_ERROR)
    with raises(asyncio.CancelledError) as info:
        await fetch_multiple(fetcher, range(6), range(6))
    assert info.value.args[0] == "any"


@mark.asyncio
async def test_fetch_multiple_common_error():
    fetcher = AsyncMock(side_effect=TASKS_COMMON_ERROR)
    with raises(ValidationError) as info:
        await fetch_multiple(fetcher, range(6), range(6))
    assert info.value.errors()[0]["type"] == "missing"
    assert info.value.errors()[0]["msg"] == "Field required"
