import pytest

from app.core.common.messages import (
    INVALID_KEYWORD,
    INVALID_KEYWORDS_LENGTH,
    MISSING_API_KEY,
    MISSING_KEYWORDS,
)
from app.framework.exceptions import Unauthorized, UnprocessableContent
from tests.helpers.models import Request
from tests.mocks.fixtures import QUERY_PARAMS


@pytest.mark.asyncio
async def test_request_params():
    request = Request(api_key="any", keywords="any,any")
    response = await QUERY_PARAMS(request)
    assert response.equals("any", ["any", "any"])


@pytest.mark.asyncio
async def test_missing_request_api_key():
    with pytest.raises(Unauthorized) as error:
        await QUERY_PARAMS(Request(keywords="any,any"))
    assert error.value.status_code == 401
    assert error.value.message == MISSING_API_KEY


@pytest.mark.asyncio
async def test_header_api_key_and_request_keywords():
    request = Request(keywords="any,any")
    response = await QUERY_PARAMS(request, "any")
    assert response.equals("any", ["any", "any"])


@pytest.mark.asyncio
async def test_missing_keywords():
    with pytest.raises(UnprocessableContent) as error:
        await QUERY_PARAMS(Request(), "any")
    assert error.value.status_code == 422
    assert error.value.message == MISSING_KEYWORDS


@pytest.mark.asyncio
async def test_invalid_keywords_length():
    with pytest.raises(UnprocessableContent) as error:
        await QUERY_PARAMS(Request(), "any", ["any"])
    assert error.value.status_code == 422
    assert error.value.message == INVALID_KEYWORDS_LENGTH


@pytest.mark.asyncio
async def test_blank_space_keywords():
    with pytest.raises(UnprocessableContent) as error:
        await QUERY_PARAMS(Request(), "any", [", ,     "])
    assert error.value.status_code == 422
    assert error.value.message == INVALID_KEYWORD


@pytest.mark.asyncio
async def test_invalid_keywords_pattern():
    with pytest.raises(UnprocessableContent) as error:
        await QUERY_PARAMS(Request(), "any", ["f@3f!sH%3P,f@3f!sH%3P"])
    assert error.value.status_code == 422
    assert error.value.message == INVALID_KEYWORD


@pytest.mark.asyncio
async def test_header_params():
    response = await QUERY_PARAMS(Request(), "any", ["any", "any"])
    assert response.equals("any", ["any", "any"])
