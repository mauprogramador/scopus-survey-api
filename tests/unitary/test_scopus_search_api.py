from asyncio import CancelledError

from pytest import mark, raises
from pytest_mock import MockerFixture as Mocker

from src.adapters.gateway.scopus_search_api import (
    ProgressBar,
    ScopusResponse,
    ScopusSearchAPI,
)
from src.core.common.types import ResponseBundle
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import (
    NotFound,
    ScopusAPIError,
    ServiceUnavailable,
)
from tests.conftest import assert_http_error
from tests.mocks.errors import MORE_CANCELLED
from tests.mocks.helpers import Patch, fqn, search_fix
from tests.mocks.raw import HTTP_404, HTTP_429, HTTP_502, HTTP_503
from tests.mocks.unitary import (
    FOUR_KEYWORDS,
    MORE_PAGES_FULL_RESULTS,
    MORE_PAGES_PARTIAL_RESULTS,
    ONE_PAGE_FULL_RESULTS,
    ONE_PAGE_ONE_RESULT,
    SEARCH_EXACT_QUOTA_MORE_RESULTS,
    SEARCH_EXACT_QUOTA_ONE_RESULT,
    SEARCH_EXACT_QUOTA_TWO_RESULTS,
    SEARCH_NO_QUOTA_MORE_RESULTS,
    SEARCH_NO_QUOTA_TWO_RESULTS,
    SEARCH_NOT_FOUND,
    SEARCH_QUOTA_EXCEEDED,
    SURVEY_MAP,
    SURVEY_NOT_FOUND,
    SURVEY_RESULTS,
    TWO_KEYWORDS,
    TWO_PAGES_FULL_RESULTS,
    TWO_PAGES_PARTIAL_RESULTS,
)


STEP = Patch(ScopusSearchAPI, ProgressBar(0).step)


@mark.asyncio
async def test_survey_two_keywords():
    fix = search_fix(SURVEY_RESULTS[:3])
    results = await fix.api.survey_totals_found(TWO_KEYWORDS)
    assert len(results) == 3 and fix.req.call_count == 3
    assert sum(item["total"] for item in results) != 0

    for item in results:
        search_results = SURVEY_MAP[item["index"]].data["search-results"]
        assert search_results["opensearch:totalResults"] == str(item["total"])


@mark.asyncio
async def test_survey_four_keywords():
    fix = search_fix(SURVEY_RESULTS)
    results = await fix.api.survey_totals_found(FOUR_KEYWORDS)
    assert len(results) == 15 and fix.req.call_count == 15
    assert sum(item["total"] for item in results) != 0

    for item in results:
        search_results = SURVEY_MAP[item["index"]].data["search-results"]
        assert search_results["opensearch:totalResults"] == str(item["total"])


@mark.asyncio
async def test_survey_not_found():
    fix = search_fix(SURVEY_NOT_FOUND)
    results = await fix.api.survey_totals_found(TWO_KEYWORDS)
    assert len(results) == 3 and fix.req.call_count == 3
    assert sum(item["total"] for item in results) == 0


@mark.asyncio
async def test_survey_cancelled_error(mocker: Mocker):
    spy = mocker.spy(ScopusResponse, "validate_search")
    fix = search_fix(SURVEY_RESULTS)
    mocker.patch(**STEP(MORE_CANCELLED))
    with raises(ServiceUnavailable) as info:
        await fix.api.survey_totals_found(FOUR_KEYWORDS)
    assert_http_error(info, HTTP_503, ExcMsg.CANCELLED_ERROR)
    assert fix.req.call_count == 15 and spy.call_count == 3
    assert info.value.errors[0]["type"] == fqn(CancelledError)
    assert info.value.errors[0]["message"] == "any"


@mark.asyncio
async def test_search_one_page_one_result():
    fix = search_fix(ONE_PAGE_ONE_RESULT)
    await fix.api.search_articles(None)
    assert len(fix.state.entry) == 1 and fix.req.call_count == 1
    assert fix.state.total_results == 1 and fix.state.items_per_page == 1
    assert fix.state.pages_count == 1


@mark.asyncio
async def test_search_one_page_full_results():
    fix = search_fix(ONE_PAGE_FULL_RESULTS)
    await fix.api.search_articles(None)
    assert len(fix.state.entry) == 1 and fix.req.call_count == 1
    assert fix.state.total_results == 25 and fix.state.items_per_page == 25
    assert fix.state.pages_count == 1


@mark.asyncio
async def test_search_two_pages_partial_results():
    fix = search_fix(TWO_PAGES_PARTIAL_RESULTS)
    await fix.api.search_articles(None)
    assert len(fix.state.entry) == 2 and fix.req.call_count == 2
    assert fix.state.total_results == 30 and fix.state.items_per_page == 25
    assert fix.state.pages_count == 2


@mark.asyncio
async def test_search_two_pages_full_results():
    fix = search_fix(TWO_PAGES_FULL_RESULTS)
    await fix.api.search_articles(None)
    assert len(fix.state.entry) == 2 and fix.req.call_count == 2
    assert fix.state.total_results == 50 and fix.state.items_per_page == 25
    assert fix.state.pages_count == 2


@mark.asyncio
async def test_search_more_pages_partial_results():
    fix = search_fix(MORE_PAGES_PARTIAL_RESULTS)
    await fix.api.search_articles(None)
    assert len(fix.state.entry) == 7 and fix.req.call_count == 7
    assert fix.state.total_results == 151 and fix.state.items_per_page == 25
    assert fix.state.pages_count == 7


@mark.asyncio
async def test_search_more_pages_full_results():
    fix = search_fix(MORE_PAGES_FULL_RESULTS)
    await fix.api.search_articles(None)
    assert len(fix.state.entry) == 7 and fix.req.call_count == 7
    assert fix.state.total_results == 175 and fix.state.items_per_page == 25
    assert fix.state.pages_count == 7


@mark.asyncio
async def test_search_not_found():
    fix = search_fix(SEARCH_NOT_FOUND)
    with raises(NotFound) as info:
        await fix.api.search_articles(None)
    assert info.value.status_code == HTTP_404 and fix.req.call_count == 1
    assert info.value.message == ExcMsg.ARTICLES_NOT_FOUND


@mark.asyncio
@mark.parametrize(
    "response,count,total,per_page",
    [
        (SEARCH_EXACT_QUOTA_ONE_RESULT, 1, 1, 1),
        (SEARCH_EXACT_QUOTA_TWO_RESULTS, 2, 26, 25),
        (SEARCH_EXACT_QUOTA_MORE_RESULTS, 7, 151, 25),
    ],
    ids=["One result", "Two results", "More results"],
)
async def test_search_exact_quota_limit(
    response: list[ResponseBundle],
    count: int,
    total: int,
    per_page: int,
):
    fix = search_fix(response)
    await fix.api.search_articles(None)
    assert len(fix.state.entry) == count and fix.req.call_count == count
    assert fix.state.total_results == total
    assert fix.state.items_per_page == per_page
    assert fix.state.pages_count == count
    assert fix.details.search_quota[0].remaining == 0


@mark.asyncio
@mark.parametrize(
    "response,count,total,per_page",
    [
        (SEARCH_NO_QUOTA_TWO_RESULTS, 1, 1, 25),
        (SEARCH_NO_QUOTA_MORE_RESULTS, 4, 76, 25),
    ],
    ids=["Two results", "More results"],
)
async def test_search_insufficient_quota(
    response: list[ResponseBundle],
    count: int,
    total: int,
    per_page: int,
):
    fix = search_fix(response)
    await fix.api.search_articles(None)
    assert len(fix.state.entry) == count and fix.req.call_count == count
    assert fix.state.total_results == total
    assert fix.state.items_per_page == per_page
    assert fix.state.pages_count == count
    assert fix.details.search_quota[0].remaining == 0


@mark.asyncio
async def test_search_quota_exceeded():
    fix = search_fix(SEARCH_QUOTA_EXCEEDED)
    with raises(ScopusAPIError) as info:
        await fix.api.search_articles(None)
    assert_http_error(info, HTTP_502, "any")
    assert len(info.value.errors) == 2 and fix.req.call_count == 1
    assert info.value.errors[0]["status"] == HTTP_429.phrase
    assert info.value.errors[0]["status_code"] == HTTP_429


@mark.asyncio
async def test_search_cancelled_error(mocker: Mocker):
    spy = mocker.spy(ScopusResponse, "validate_search")
    fix = search_fix(MORE_PAGES_PARTIAL_RESULTS)
    mocker.patch(**STEP(MORE_CANCELLED))
    with raises(ServiceUnavailable) as info:
        await fix.api.search_articles(None)
    assert_http_error(info, HTTP_503, ExcMsg.CANCELLED_ERROR)
    assert fix.req.call_count == 7 and spy.call_count == 4
    assert info.value.errors[0]["type"] == fqn(CancelledError)
    assert info.value.errors[0]["message"] == "any"
