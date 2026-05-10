from asyncio import CancelledError
from unittest.mock import AsyncMock, MagicMock

from pytest import mark, raises
from pytest_mock import MockerFixture as Mocker

from src.adapters.gateway.scopus_search_api import ScopusSearchAPI
from src.adapters.helpers.http_client import HTTPClient
from src.adapters.helpers.scopus_response import ScopusResponse
from src.adapters.helpers.url_builder import URLBuilder
from src.core.common.error_messages import (
    ARTICLES_NOT_FOUND,
    CANCELLED_ERROR,
    QUOTA_EXCEEDED,
)
from src.core.data.serializers import ScopusSearch
from src.core.data.survey_details import SurveyDetails
from src.core.domain.http_exceptions import (
    NotFound,
    ServiceUnavailable,
    TooManyRequests,
)
from src.utils.progress_bar import ProgressBar
from tests.conftest import assert_http_error
from tests.mocks.helpers import fqn
from tests.mocks.raw import (
    HTTP_404,
    HTTP_429,
    HTTP_503,
    LOG_NO_QUOTA,
    LOG_ONE_QUOTA,
    LOG_QUOTA,
    RAW_SEARCH_NOT_FOUND,
)
from tests.mocks.unitary import (
    FOUR_KEYWORDS,
    MORE_PAGES_FULL_RESULTS,
    MORE_PAGES_NO_QUOTA,
    MORE_PAGES_ONE_QUOTA,
    MORE_PAGES_PARTIAL_RESULTS,
    ONE_PAGE_FULL_RESULTS,
    ONE_PAGE_ONE_RESULT,
    SURVEY_MAP,
    SURVEY_RESULTS,
    TWO_KEYWORDS,
    TWO_PAGES_FULL_RESULTS,
    TWO_PAGES_PARTIAL_RESULTS,
)


STEP = fqn(ProgressBar.step)


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
    assert_http_error(info, HTTP_503, CANCELLED_ERROR)
    assert fix.req.call_count == 15 and spy.call_count == 3
    assert info.value.errors[0]["type"] == fqn(CancelledError)
    assert info.value.errors[0]["detail"] == "any"


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
    assert info.value.message == ARTICLES_NOT_FOUND


@mark.asyncio
async def test_search_one_last_quota(mocker: Mocker):
    SURVEY_DETAILS.search_quota = LOG_ONE_QUOTA
    mock = mocker.patch(VALIDATE_SEARCH, side_effect=MORE_PAGES_ONE_QUOTA)
    result = await SEARCH_API.search_articles(None)
    assert len(result.entry) == 50 and mock.call_count == 2


@mark.asyncio
async def test_search_no_remaining_quota(mocker: Mocker):
    SURVEY_DETAILS.search_quota = LOG_NO_QUOTA
    mock = mocker.patch(VALIDATE_SEARCH, return_value=ONE_PAGE_FULL_RESULTS)
    result = await SEARCH_API.search_articles(None)
    assert len(result.entry) == 25 and mock.call_count == 1


@mark.asyncio
async def test_search_quota_exceeded():
    fix = search_fix(SEARCH_QUOTA_EXCEEDED)
    with raises(ScopusAPIError) as info:
        await fix.api.search_articles(None)
    assert_http_error(info, HTTP_502, ScopusCode.QUOTA)
    assert fix.req.call_count == 1


@mark.asyncio
async def test_search_cancelled_error(mocker: Mocker):
    spy = mocker.spy(ScopusResponse, "validate_search")
    fix = search_fix(MORE_PAGES_PARTIAL_RESULTS)
    mocker.patch(**STEP(MORE_CANCELLED))
    with raises(ServiceUnavailable) as info:
        await fix.api.search_articles(None)
    assert_http_error(info, HTTP_503, CANCELLED_ERROR)
    assert fix.req.call_count == 7 and spy.call_count == 4
    assert info.value.errors[0]["type"] == fqn(CancelledError)
    assert info.value.errors[0]["detail"] == "any"
