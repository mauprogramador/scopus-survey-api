# mypy: disable-error-code="union-attr"
import asyncio
from unittest.mock import PropertyMock

from pydantic import ValidationError
from pytest import mark, raises
from pytest_mock import MockerFixture as Mocker

from src.adapters.gateway.scopus_search_api import (
    ScopusSearchAPI,
    progress_bar,
    validate_search_response,
)
from src.core.common.types import ResponseBundle
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import (
    HTTPError,
    InternalError,
    NotFound,
    ScopusAPIError,
)
from tests.conftest import assert_http_error
from tests.mocks.errors import (
    TASKS_CANCELLED_ERROR,
    TASKS_COMMON_ERROR,
    TASKS_HTTP_ERROR,
)
from tests.mocks.helpers import MockProgressBar, MockState, fqn, search_fix
from tests.mocks.raw import HTTP_400, HTTP_404, HTTP_429, HTTP_500, HTTP_502
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


SEARCH_RES = fqn(ScopusSearchAPI, validate_search_response)
PBAR = fqn(ScopusSearchAPI, progress_bar)


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
async def test_survey_no_tasks():
    fix = search_fix(SURVEY_RESULTS[:3])
    with raises(HTTPError) as info:
        await fix.api.survey_totals_found({})
    assert_http_error(info, HTTP_500, ExcMsg.INTERNAL_ERROR)
    fix.req.assert_not_called()


@mark.asyncio
async def test_survey_http_error(mocker: Mocker):
    spy = mocker.patch(SEARCH_RES, wraps=validate_search_response)
    fix = search_fix(SURVEY_RESULTS[:7])
    mocker.patch(PBAR, MockProgressBar(TASKS_HTTP_ERROR))
    with raises(HTTPError) as info:
        await fix.api.survey_totals_found(TWO_KEYWORDS)
    assert_http_error(info, HTTP_400, ExcMsg.INTERNAL_ERROR)
    # _get_article has less CPU executions
    assert fix.req.call_count == 3 and spy.call_count == 3
    assert info.value.details[0]["type"] == fqn(ValueError)
    assert info.value.details[0]["message"] == "any"


@mark.asyncio
async def test_survey_cancelled_error(mocker: Mocker):
    spy = mocker.patch(SEARCH_RES, wraps=validate_search_response)
    fix = search_fix(SURVEY_RESULTS[:7])
    mocker.patch(PBAR, MockProgressBar(TASKS_CANCELLED_ERROR))
    with raises(InternalError) as info:
        await fix.api.survey_totals_found(FOUR_KEYWORDS)
    assert_http_error(info, HTTP_500, ExcMsg.CANCELLED_ERROR)
    # TaskGroup swallows CancelledError
    assert fix.req.call_count == 15 and spy.call_count in (6, 7)
    assert info.value.details[0]["type"] == fqn(asyncio.CancelledError)
    assert info.value.details[0]["message"] == repr(asyncio.CancelledError())


@mark.asyncio
async def test_survey_operational_error(mocker: Mocker):
    spy = mocker.patch(SEARCH_RES, wraps=validate_search_response)
    fix = search_fix(SURVEY_RESULTS[:7])
    mocker.patch(PBAR, MockProgressBar(TASKS_COMMON_ERROR))
    with raises(InternalError) as info:
        await fix.api.survey_totals_found(TWO_KEYWORDS)
    assert_http_error(info, HTTP_500, ExcMsg.CANCELLED_ERROR)
    # _get_article has less CPU executions
    assert fix.req.call_count == 3 and spy.call_count == 3
    assert info.value.details[0]["type"] == fqn(ValidationError)
    assert info.value.details[0]["message"] is not None


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
    "res_mock,count,total,per_page",
    [
        (SEARCH_EXACT_QUOTA_ONE_RESULT, 1, 1, 1),
        (SEARCH_EXACT_QUOTA_TWO_RESULTS, 2, 26, 25),
        (SEARCH_EXACT_QUOTA_MORE_RESULTS, 7, 151, 25),
    ],
    ids=["One result", "Two results", "More results"],
)
async def test_search_exact_quota_limit(
    res_mock: list[ResponseBundle],
    count: int,
    total: int,
    per_page: int,
):
    fix = search_fix(res_mock)
    await fix.api.search_articles(None)
    assert len(fix.state.entry) == count and fix.req.call_count == count
    assert fix.state.total_results == total
    assert fix.state.items_per_page == per_page
    assert fix.state.pages_count == count
    assert fix.details.search_quota[0].remaining == 0


@mark.asyncio
@mark.parametrize(
    "res_mock,count,total,per_page",
    [
        (SEARCH_NO_QUOTA_TWO_RESULTS, 1, 1, 25),
        (SEARCH_NO_QUOTA_MORE_RESULTS, 4, 76, 25),
    ],
    ids=["Two results", "More results"],
)
async def test_search_insufficient_quota(
    res_mock: list[ResponseBundle],
    count: int,
    total: int,
    per_page: int,
):
    fix = search_fix(res_mock)
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
    assert len(info.value.details) == 2 and fix.req.call_count == 1
    assert info.value.details[0]["status"] == HTTP_429.phrase
    assert info.value.details[0]["status_code"] == HTTP_429


@mark.asyncio
async def test_search_no_tasks(mocker: Mocker):
    fix = search_fix(MORE_PAGES_PARTIAL_RESULTS)
    mocker.patch(
        f"{fqn(MockState)}.pages_to_fetch_range",
        PropertyMock(return_value=range(0)),
    )
    with raises(HTTPError) as info:
        await fix.api.search_articles(None)
    assert_http_error(info, HTTP_500, ExcMsg.INTERNAL_ERROR)
    assert fix.req.call_count == 1


@mark.asyncio
async def test_search_http_error(mocker: Mocker):
    spy = mocker.patch(SEARCH_RES, wraps=validate_search_response)
    fix = search_fix(MORE_PAGES_PARTIAL_RESULTS)
    mocker.patch(PBAR, MockProgressBar(TASKS_HTTP_ERROR))
    with raises(HTTPError) as info:
        await fix.api.search_articles(None)
    assert_http_error(info, HTTP_400, ExcMsg.INTERNAL_ERROR)
    # _get_article has less CPU executions
    assert fix.req.call_count == 7 and spy.call_count in (6, 7)
    assert info.value.details[0]["type"] == fqn(ValueError)
    assert info.value.details[0]["message"] == "any"


@mark.asyncio
async def test_search_cancelled_error(mocker: Mocker):
    spy = mocker.patch(SEARCH_RES, wraps=validate_search_response)
    fix = search_fix(MORE_PAGES_PARTIAL_RESULTS)
    mocker.patch(PBAR, MockProgressBar(TASKS_CANCELLED_ERROR))
    with raises(InternalError) as info:
        await fix.api.search_articles(None)
    assert_http_error(info, HTTP_500, ExcMsg.CANCELLED_ERROR)
    # TaskGroup swallows CancelledError
    assert fix.req.call_count == 7 and spy.call_count == 7
    assert info.value.details[0]["type"] == fqn(asyncio.CancelledError)
    assert info.value.details[0]["message"] == "any"


@mark.asyncio
async def test_search_operational_error(mocker: Mocker):
    spy = mocker.patch(SEARCH_RES, wraps=validate_search_response)
    fix = search_fix(MORE_PAGES_PARTIAL_RESULTS)
    mocker.patch(PBAR, MockProgressBar(TASKS_COMMON_ERROR))
    with raises(InternalError) as info:
        await fix.api.search_articles(None)
    assert_http_error(info, HTTP_500, ExcMsg.CANCELLED_ERROR)
    # _get_article has less CPU executions
    assert fix.req.call_count == 7 and spy.call_count in (6, 7)
    assert info.value.details[0]["type"] == fqn(ValidationError)
    assert info.value.details[0]["message"] is not None
