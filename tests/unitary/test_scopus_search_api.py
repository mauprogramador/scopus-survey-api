from asyncio import CancelledError
from unittest.mock import AsyncMock, MagicMock

from pytest import mark, raises
from pytest_mock import MockerFixture as Mocker

from src.adapters.gateway.scopus_search_api import ScopusSearchAPI
from src.adapters.helpers.http_client import HTTPClient
from src.adapters.helpers.scopus_response import ScopusResponse
from src.adapters.helpers.url_builder import URLBuilder
from src.core.common.error_messages import ARTICLES_NOT_FOUND, CANCELLED_ERROR
from src.core.data.serializers import ScopusSearch
from src.core.data.survey_detail import SurveyDetail
from src.core.domain.http_exceptions import NotFound, ServiceUnavailable
from src.utils.progress_bar import ProgressBar
from tests.conftest import assert_http_error
from tests.mocks.helpers import fqn
from tests.mocks.raw import (
    HTTP_404,
    HTTP_503,
    RAW_SEARCH_NOT_FOUND,
)
from tests.mocks.unitary import (
    FOUR_KEYWORDS,
    MORE_PAGES_FULL_RESULTS,
    MORE_PAGES_PARTIAL_RESULTS,
    ONE_PAGE_FULL_RESULTS,
    ONE_PAGE_ONE_RESULT,
    SURVEY_MAP,
    SURVEY_RESULTS,
    TWO_KEYWORDS,
    TWO_PAGES_FULL_RESULTS,
    TWO_PAGES_PARTIAL_RESULTS,
)

SEARCH_API = ScopusSearchAPI(
    AsyncMock(spec=HTTPClient),
    MagicMock(spec=URLBuilder),
    MagicMock(spec=SurveyDetail),
)
VALIDATE_SEARCH = fqn(ScopusResponse.validate_search)
# SET_COUNT_LIMIT = fqn(ScopusSearch.set_count_limit)
STEP = fqn(ProgressBar.step)


@mark.asyncio
async def test_survey_two_keywords(mocker: Mocker):
    mock = mocker.patch(VALIDATE_SEARCH, side_effect=SURVEY_RESULTS[:3])
    results = await SEARCH_API.survey_totals_found(TWO_KEYWORDS)
    assert len(results) == 3 and mock.call_count == 3
    assert sum(item["total"] for item in results) != 0

    for item in results:
        assert SURVEY_MAP[item["index"]].total_results == item["total"]


@mark.asyncio
async def test_survey_four_keywords(mocker: Mocker):
    mock = mocker.patch(VALIDATE_SEARCH, side_effect=SURVEY_RESULTS)
    results = await SEARCH_API.survey_totals_found(FOUR_KEYWORDS)
    assert len(results) == 15 and mock.call_count == 15
    assert sum(item["total"] for item in results) != 0

    for item in results:
        assert SURVEY_MAP[item["index"]].total_results == item["total"]


@mark.asyncio
async def test_survey_not_found(mocker: Mocker):
    mock = mocker.patch(
        VALIDATE_SEARCH,
        side_effect=[ScopusSearch(**RAW_SEARCH_NOT_FOUND)] * 3,
    )
    results = await SEARCH_API.survey_totals_found(TWO_KEYWORDS)
    assert len(results) == 3 and mock.call_count == 3
    assert sum(item["total"] for item in results) == 0


@mark.asyncio
async def test_survey_cancelled_error(mocker: Mocker):
    mocker.patch(STEP, side_effect=[None, None, CancelledError("any")])
    mock = mocker.patch(VALIDATE_SEARCH, side_effect=SURVEY_RESULTS)
    with raises(ServiceUnavailable) as info:
        await SEARCH_API.survey_totals_found(FOUR_KEYWORDS)
    assert mock.call_count == 3
    assert_http_error(info, HTTP_503, CANCELLED_ERROR)
    assert info.value.errors[0]["type"] == fqn(CancelledError)
    assert info.value.errors[0]["detail"] == "any"


@mark.asyncio
async def test_search_one_page_one_result(mocker: Mocker):
    mock = mocker.patch(VALIDATE_SEARCH, return_value=ONE_PAGE_ONE_RESULT)
    result = await SEARCH_API.search_articles(None)
    assert len(result) == 1 and mock.call_count == 1


@mark.asyncio
async def test_search_one_page_full_results(mocker: Mocker):
    mock = mocker.patch(VALIDATE_SEARCH, return_value=ONE_PAGE_FULL_RESULTS)
    result = await SEARCH_API.search_articles(None)
    assert len(result) == 25 and mock.call_count == 1


@mark.asyncio
async def test_search_two_pages_partial_results(mocker: Mocker):
    mock = mocker.patch(VALIDATE_SEARCH, side_effect=TWO_PAGES_PARTIAL_RESULTS)
    result = await SEARCH_API.search_articles(None)
    assert len(result) == 30 and mock.call_count == 2


@mark.asyncio
async def test_search_two_pages_full_results(mocker: Mocker):
    mock = mocker.patch(VALIDATE_SEARCH, side_effect=TWO_PAGES_FULL_RESULTS)
    result = await SEARCH_API.search_articles(None)
    assert len(result) == 50 and mock.call_count == 2


@mark.asyncio
async def test_search_more_pages_partial_results(mocker: Mocker):
    # mocker.patch(SET_COUNT_LIMIT)
    mock = mocker.patch(
        VALIDATE_SEARCH, side_effect=MORE_PAGES_PARTIAL_RESULTS
    )
    result = await SEARCH_API.search_articles(None)
    assert len(result) == 151 and mock.call_count == 7


@mark.asyncio
async def test_search_more_pages_full_results(mocker: Mocker):
    # mocker.patch(SET_COUNT_LIMIT)
    mock = mocker.patch(VALIDATE_SEARCH, side_effect=MORE_PAGES_FULL_RESULTS)
    result = await SEARCH_API.search_articles(None)
    assert len(result) == 175 and mock.call_count == 7


@mark.asyncio
async def test_search_not_found(mocker: Mocker):
    mock = mocker.patch(
        VALIDATE_SEARCH,
        return_value=ScopusSearch(**RAW_SEARCH_NOT_FOUND),
    )
    with raises(NotFound) as info:
        await SEARCH_API.search_articles(None)
    assert info.value.status_code == HTTP_404 and mock.call_count == 1
    assert info.value.message == ARTICLES_NOT_FOUND


# @mark.asyncio
# async def test_search_count_limit_default(mocker: Mocker):
#     ?????


@mark.asyncio
async def test_search_cancelled_error(mocker: Mocker):
    mocker.patch(STEP, side_effect=[None, None, CancelledError("any")])
    mock = mocker.patch(
        VALIDATE_SEARCH,
        side_effect=MORE_PAGES_PARTIAL_RESULTS,
    )
    with raises(ServiceUnavailable) as info:
        await SEARCH_API.search_articles(None)
    assert_http_error(info, HTTP_503, CANCELLED_ERROR)
    assert mock.call_count == 4
    assert info.value.errors[0]["type"] == fqn(CancelledError)
    assert info.value.errors[0]["detail"] == "any"
