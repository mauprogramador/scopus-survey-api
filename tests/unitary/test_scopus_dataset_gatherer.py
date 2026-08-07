import math
from typing import Any
from unittest.mock import AsyncMock

from pytest import mark, raises

from src.adapters.gateway.context import ScopusContext
from src.adapters.gateway.scopus_dataset_gatherer import (
    ScopusDatasetGatherer,
    fetch_multiple,
    validate_abstract_response,
)
from src.adapters.serializers.query_params import SurveyParams
from src.adapters.types import ResponseBundle
from src.core.domain.types import ExcMsg
from src.core.domain.exceptions import NotFound, ScopusAPIError
from src.infra.config.scopus import MAX_ITEMS_PER_PAGE, QUOTA_ERROR_CODE
from src.infra.http.http_client import HTTPClient
from tests.conftest import assert_http_error
from tests.mocks.helpers import fqn
from tests.mocks.raw import ALIAS_SEARCH_PARAMS, HTTP_404, HTTP_429, HTTP_502
from tests.mocks.unitary import (
    ABSTRACT_QUOTA_EXCEEDED,
    EXACT_QUOTA_MORE_ABSTRACTS,
    EXACT_QUOTA_MORE_PAGES,
    EXACT_QUOTA_MORE_RESULTS,
    EXACT_QUOTA_ONE_ABSTRACT,
    EXACT_QUOTA_ONE_PAGE,
    EXACT_QUOTA_ONE_RESULT,
    EXACT_QUOTA_TWO_ABSTRACTS,
    EXACT_QUOTA_TWO_PAGES,
    EXACT_QUOTA_TWO_RESULTS,
    MORE_PAGES_FULL_ABSTRACTS,
    MORE_PARTIAL_PAGES_ABSTRACTS,
    NO_QUOTA_MORE_ABSTRACTS,
    NO_QUOTA_MORE_PAGES,
    NO_QUOTA_MORE_RESULTS,
    NO_QUOTA_TWO_ABSTRACTS,
    NO_QUOTA_TWO_PAGES,
    NO_QUOTA_TWO_RESULTS,
    ONE_PAGE_FULL_ABSTRACTS,
    ONE_PAGE_ONE_ABSTRACT,
    ONE_PAGE_TWO_ABSTRACTS,
    SEARCH_NOT_FOUND,
    SEARCH_QUOTA_EXCEEDED,
    TWO_PAGES_FULL_ABSTRACTS,
    TWO_PARTIAL_PAGES_ABSTRACTS,
)


ABSTRACT_RES = fqn(ScopusDatasetGatherer, validate_abstract_response)
FETCH_MULTIPLE = fqn(ScopusDatasetGatherer, fetch_multiple)
PARAMS = SurveyParams(**ALIAS_SEARCH_PARAMS)
CONTEXT = fqn(ScopusDatasetGatherer, ScopusContext)


def _fixt(value: Any | Exception) -> tuple[ScopusDatasetGatherer, AsyncMock]:
    if isinstance(value, (list, BaseException)):
        mock_api_call = AsyncMock(HTTPClient.api_call, side_effect=value)
    else:
        mock_api_call = AsyncMock(HTTPClient.api_call, return_value=value)
    mock_client = AsyncMock(HTTPClient, api_call=mock_api_call)
    gateway = ScopusDatasetGatherer(mock_client)
    return gateway, mock_api_call


@mark.asyncio
async def test_gather_one_page_one_abstract():
    gateway, api_call = _fixt(ONE_PAGE_ONE_ABSTRACT)
    results, details = await gateway.fetch(PARAMS)
    ctx = gateway._ctx  # pylint: disable=w0212

    assert len(results) == 1 and api_call.call_count == 2
    assert len(ctx.entry) == 1 and ctx.items_per_page == 1
    assert len(ctx.abstracts) == 1 and ctx.total_results == 1
    assert details.pages_count == 1 and details.total_retrieved == 1


@mark.asyncio
async def test_gather_one_page_two_abstracts():
    gateway, api_call = _fixt(ONE_PAGE_TWO_ABSTRACTS)
    results, details = await gateway.fetch(PARAMS)
    ctx = gateway._ctx  # pylint: disable=w0212

    assert len(results) == 2 and api_call.call_count == 3
    assert len(ctx.entry) == 2 and ctx.items_per_page == 2
    assert len(ctx.abstracts) == 2 and ctx.total_results == 2
    assert details.pages_count == 1 and details.total_retrieved == 2


@mark.asyncio
async def test_gather_one_page_full_abstracts():
    gateway, api_call = _fixt(ONE_PAGE_FULL_ABSTRACTS)
    results, details = await gateway.fetch(PARAMS)
    ctx = gateway._ctx  # pylint: disable=w0212

    assert len(results) == 25 and api_call.call_count == 26
    assert len(ctx.entry) == 25 and ctx.items_per_page == 25
    assert len(ctx.abstracts) == 25 and ctx.total_results == 25
    assert details.pages_count == 1 and details.total_retrieved == 25


@mark.asyncio
async def test_gather_two_pages_partial_abstracts():
    gateway, api_call = _fixt(TWO_PARTIAL_PAGES_ABSTRACTS)
    results, details = await gateway.fetch(PARAMS)
    ctx = gateway._ctx  # pylint: disable=w0212

    assert len(results) == 30 and api_call.call_count == 32
    assert len(ctx.entry) == 30 and ctx.items_per_page == 25
    assert len(ctx.abstracts) == 30 and ctx.total_results == 30
    assert details.pages_count == 2 and details.total_retrieved == 30


@mark.asyncio
async def test_gather_two_pages_full_abstracts():
    gateway, api_call = _fixt(TWO_PAGES_FULL_ABSTRACTS)
    results, details = await gateway.fetch(PARAMS)
    ctx = gateway._ctx  # pylint: disable=w0212

    assert len(results) == 50 and api_call.call_count == 52
    assert len(ctx.entry) == 50 and ctx.items_per_page == 25
    assert len(ctx.abstracts) == 50 and ctx.total_results == 50
    assert details.pages_count == 2 and details.total_retrieved == 50


@mark.asyncio
async def test_gather_more_pages_partial_abstracts():
    gateway, api_call = _fixt(MORE_PARTIAL_PAGES_ABSTRACTS)
    results, details = await gateway.fetch(PARAMS)
    ctx = gateway._ctx  # pylint: disable=w0212

    assert len(results) == 151 and api_call.call_count == 158
    assert len(ctx.entry) == 151 and ctx.items_per_page == 25
    assert len(ctx.abstracts) == 151 and ctx.total_results == 151
    assert details.pages_count == 7 and details.total_retrieved == 151


@mark.asyncio
async def test_gather_more_pages_full_abstracts():
    gateway, api_call = _fixt(MORE_PAGES_FULL_ABSTRACTS)
    results, details = await gateway.fetch(PARAMS)
    ctx = gateway._ctx  # pylint: disable=w0212

    assert len(results) == 175 and api_call.call_count == 182
    assert len(ctx.entry) == 175 and ctx.items_per_page == 25
    assert len(ctx.abstracts) == 175 and ctx.total_results == 175
    assert details.pages_count == 7 and details.total_retrieved == 175


@mark.asyncio
async def test_gather_not_found():
    gateway, api_call = _fixt(SEARCH_NOT_FOUND)
    ctx = gateway._ctx  # pylint: disable=w0212

    with raises(NotFound) as info:
        await gateway.fetch(PARAMS)

    assert info.value.status_code == HTTP_404 and api_call.call_count == 1
    assert info.value.message == ExcMsg.ARTICLES_NOT_FOUND

    assert len(ctx.entry) == 0 and ctx.items_per_page == 0
    assert not ctx.total_results and ctx.search_headers is not None


@mark.asyncio
@mark.parametrize(
    "res_mock,total,has_search_quota,has_abstract_quota",
    [
        (EXACT_QUOTA_ONE_ABSTRACT, 1, True, False),
        (EXACT_QUOTA_ONE_PAGE, 1, False, True),
        (EXACT_QUOTA_ONE_RESULT, 1, False, False),
        (EXACT_QUOTA_TWO_ABSTRACTS, 2, True, False),
        (EXACT_QUOTA_TWO_PAGES, 26, False, True),
        (EXACT_QUOTA_TWO_RESULTS, 26, False, False),
        (EXACT_QUOTA_MORE_ABSTRACTS, 151, True, False),
        (EXACT_QUOTA_MORE_PAGES, 151, False, True),
        (EXACT_QUOTA_MORE_RESULTS, 151, False, False),
    ],
    ids=[
        "One abstract",
        "One page",
        "One result",
        "Two abstracts",
        "Two pages",
        "Two results",
        "More abstracts",
        "More pages",
        "More results",
    ],
)
async def test_gather_exact_quota_limit(
    res_mock: list[ResponseBundle],
    total: int,
    has_search_quota: bool,
    has_abstract_quota: bool,
):
    gateway, api_call = _fixt(res_mock)
    results, details = await gateway.fetch(PARAMS)
    ctx = gateway._ctx  # pylint: disable=w0212

    count = math.ceil(total / MAX_ITEMS_PER_PAGE)
    per_page = min(total, MAX_ITEMS_PER_PAGE)

    assert len(results) == total and api_call.call_count == len(res_mock)
    assert len(ctx.entry) == total and ctx.items_per_page == per_page
    assert len(ctx.abstracts) == total and ctx.total_results == total
    assert details.pages_count == count and details.total_retrieved == total

    assert details.search_headers.remaining is not None
    assert details.abstract_headers.remaining is not None

    if has_search_quota:
        assert details.search_headers.remaining > 0
    else:
        assert details.search_headers.remaining == 0

    if has_abstract_quota:
        assert details.abstract_headers.remaining > 0
    else:
        assert details.abstract_headers.remaining == 0


@mark.asyncio
@mark.parametrize(
    "res_mock,total,entry,has_search_quota,has_abstract_quota",
    [
        (NO_QUOTA_TWO_ABSTRACTS, 1, 2, True, False),
        (NO_QUOTA_TWO_PAGES, 25, 25, False, True),
        (NO_QUOTA_TWO_RESULTS, 1, 25, False, False),
        (NO_QUOTA_MORE_ABSTRACTS, 4, 7, True, False),
        (NO_QUOTA_MORE_PAGES, 100, 100, False, True),
        (NO_QUOTA_MORE_RESULTS, 100, 100, False, False),
    ],
    ids=[
        "Two abstracts",
        "Two pages",
        "Two results",
        "More abstracts",
        "More pages",
        "More results",
    ],
)
async def test_gather_insufficient_quota(
    res_mock: list[ResponseBundle],
    entry: int,
    total: int,
    has_search_quota: bool,
    has_abstract_quota: bool,
):
    gateway, api_call = _fixt(res_mock)
    results, details = await gateway.fetch(PARAMS)
    ctx = gateway._ctx  # pylint: disable=w0212

    count = math.ceil(entry / MAX_ITEMS_PER_PAGE)
    per_page = min(entry, MAX_ITEMS_PER_PAGE)

    assert len(results) == total and api_call.call_count == len(res_mock)
    assert len(ctx.entry) == entry and ctx.items_per_page == per_page
    assert len(ctx.abstracts) == total and ctx.total_results == total
    assert details.pages_count == count and details.total_retrieved == total

    assert details.search_headers.remaining is not None
    assert details.abstract_headers.remaining is not None

    if has_search_quota:
        assert details.search_headers.remaining > 0
    else:
        assert details.search_headers.remaining == 0

    if has_abstract_quota:
        assert details.abstract_headers.remaining > 0
    else:
        assert details.abstract_headers.remaining == 0


@mark.asyncio
async def test_gather_search_quota_exceeded():
    gateway, api_call = _fixt(SEARCH_QUOTA_EXCEEDED)
    ctx = gateway._ctx  # pylint: disable=w0212

    with raises(ScopusAPIError) as info:
        await gateway.fetch(PARAMS)

    assert_http_error(info, HTTP_502, "any")
    assert api_call.call_count == 1
    assert info.value.details[0]["status_code"] == HTTP_429
    assert info.value.details[0]["error_code"] == QUOTA_ERROR_CODE

    assert len(ctx.entry) == 0 and len(ctx.abstracts) == 0
    assert not ctx.search_headers and not ctx.abstract_headers


@mark.asyncio
async def test_gather_abstract_quota_exceeded():
    gateway, api_call = _fixt(ABSTRACT_QUOTA_EXCEEDED)
    ctx = gateway._ctx  # pylint: disable=w0212

    with raises(ScopusAPIError) as info:
        await gateway.fetch(PARAMS)

    assert_http_error(info, HTTP_502, "any")
    assert api_call.call_count == 2
    assert info.value.details[0]["status_code"] == HTTP_429
    assert info.value.details[0]["error_code"] == QUOTA_ERROR_CODE

    assert len(ctx.entry) == 1 and len(ctx.abstracts) == 0
    assert ctx.search_headers and not ctx.abstract_headers
