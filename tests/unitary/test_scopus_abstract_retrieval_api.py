from asyncio import CancelledError

from pytest import mark, raises
from pytest_mock import MockerFixture as Mocker

from src.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from src.adapters.helpers.http_client import HTTPClient
from src.adapters.helpers.scopus_response import ScopusResponse
from src.adapters.helpers.url_builder import URLBuilder
from src.core.common.error_messages import CANCELLED_ERROR, QUOTA_EXCEEDED
from src.core.data.enums import Column
from src.core.data.survey_details import SurveyDetails
from src.core.domain.http_exceptions import ServiceUnavailable, TooManyRequests
from src.utils.progress_bar import ProgressBar
from tests.conftest import assert_http_error
from tests.mocks.helpers import fqn, results_mock
from tests.mocks.raw import (
    API_KEY,
    HTTP_429,
    HTTP_503,
    LOG_NO_QUOTA,
    LOG_ONE_QUOTA,
    LOG_QUOTA,
)
from tests.mocks.unitary import (
    ONE_ABSTRACT,
    ONE_ABSTRACT_AUTHORS,
    ONE_ABSTRACT_FULL,
)


STEP = Patch(ScopusAbstractRetrievalAPI, ProgressBar(0).step)


@mark.asyncio
async def test_retrieve_one_partial_abstract():
    fix = abstract_fix(ONE_ABSTRACT, search_raw(1))
    result = await fix.api.retrieve_abstracts(API_KEY)
    assert result.shape == (1, 11) and fix.req.call_count == 1
    assert result[Column.AUTHORS].iloc[0] == "any_author"
    assert len(fix.state.entry) == 1 and fix.state.total_results == 1
    assert fix.state.total_abstracts == len(fix.state.abstracts) == 1


@mark.asyncio
async def test_retrieve_one_abstract_authors():
    fix = abstract_fix(ONE_ABSTRACT_AUTHORS, search_raw(1))
    result = await fix.api.retrieve_abstracts(API_KEY)
    assert result.shape == (1, 11) and fix.req.call_count == 1
    assert result[Column.AUTHORS].iloc[0] == "any_author_1, any_author_2"
    assert len(fix.state.entry) == 1 and fix.state.total_results == 1
    assert fix.state.total_abstracts == len(fix.state.abstracts) == 1


@mark.asyncio
async def test_retrieve_one_abstract_full():
    fix = abstract_fix(ONE_ABSTRACT_FULL, search_raw(1))
    result = await fix.api.retrieve_abstracts(API_KEY)
    assert result.shape == (1, 11) and fix.req.call_count == 1
    assert result["Abstract"].iloc[0] == "any_abstract"
    assert len(fix.state.entry) == 1 and fix.state.total_results == 1
    assert fix.state.total_abstracts == len(fix.state.abstracts) == 1


@mark.asyncio
async def test_retrieve_two_abstracts():
    fix = abstract_fix(ONE_ABSTRACT, search_raw(2))
    result = await fix.api.retrieve_abstracts(API_KEY)
    assert result.shape == (2, 11) and fix.req.call_count == 2
    assert len(fix.state.entry) == 2 and fix.state.total_results == 2
    assert fix.state.total_abstracts == len(fix.state.abstracts) == 2


@mark.asyncio
async def test_retrieve_more_abstracts():
    fix = abstract_fix(ONE_ABSTRACT, search_raw(7))
    result = await fix.api.retrieve_abstracts(API_KEY)
    assert result.shape == (7, 11) and fix.req.call_count == 7
    assert len(fix.state.entry) == 7 and fix.state.total_results == 7
    assert fix.state.total_abstracts == len(fix.state.abstracts) == 7


@mark.asyncio
@mark.parametrize(
    "response,total",
    [
        (ABSTRACT_EXACT_QUOTA_ONE_RESULT, 1),
        (ABSTRACT_EXACT_QUOTA_TWO_RESULTS, 2),
        (ABSTRACT_EXACT_QUOTA_MORE_RESULTS, 7),
    ],
    ids=["One result", "Two results", "More results"],
)
async def test_retrieve_exact_quota_limit(
    response: list[ResponseBundle], total: int
):
    fix = abstract_fix(response, search_raw(total))
    result = await fix.api.retrieve_abstracts(API_KEY)
    assert result.shape == (total, 11) and fix.req.call_count == total
    assert len(fix.state.entry) == total and fix.state.total_results == total
    assert fix.state.total_abstracts == len(fix.state.abstracts) == total
    assert fix.details.abstract_quota[0].remaining == 0


@mark.asyncio
@mark.parametrize(
    "response,count,total",
    [
        (ABSTRACT_NO_QUOTA_TWO_RESULTS, 1, 26),
        (ABSTRACT_NO_QUOTA_MORE_RESULTS, 4, 151),
    ],
    ids=["Two results", "More results"],
)
async def test_retrieve_insufficient_quota(
    response: list[ResponseBundle], count: int, total: int
):
    fix = abstract_fix(response, search_raw(total, count), count)
    result = await fix.api.retrieve_abstracts(API_KEY)
    assert result.shape == (count, 11)
    assert fix.req.call_count == count
    assert len(fix.state.entry) == count and fix.state.total_results == total
    assert fix.state.total_abstracts == len(fix.state.abstracts) == count
    assert fix.details.abstract_quota[0].remaining == 0


@mark.asyncio
async def test_retrieve_quota_exceeded():
    fix = abstract_fix(ABSTRACT_QUOTA_EXCEEDED, search_raw(1))
    with raises(ScopusAPIError) as info:
        await fix.api.retrieve_abstracts(API_KEY)
    assert_http_error(info, HTTP_502, ScopusCode.QUOTA)
    assert fix.req.call_count == 1


@mark.asyncio
async def test_retrieve_cancelled_error(mocker: Mocker):
    spy = mocker.spy(ScopusResponse, "validate_abstract")
    fix = abstract_fix(ONE_ABSTRACT, search_raw(7))
    mocker.patch(**STEP(MORE_CANCELLED))
    with raises(ServiceUnavailable) as info:
        await fix.api.retrieve_abstracts(API_KEY)
    assert_http_error(info, HTTP_503, CANCELLED_ERROR)
    assert fix.req.call_count == 7 and spy.call_count == 4
    assert info.value.errors[0]["type"] == fqn(CancelledError)
    assert info.value.errors[0]["detail"] == "any"
