# mypy: disable-error-code="index"
from unittest.mock import AsyncMock

from aiohttp_retry import RetryClient
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.common.types import ResponseBundle
from src.core.data.serializers import ScopusHeaders, ScopusSearch
from src.core.data.survey_detail import SurveyDetail
from src.core.use_cases.keyword_combination_finder import (
    KeywordCombinationFinder,
)
from tests.mocks.helpers import fqn
from tests.mocks.integration import (
    COMBINATION_DETAILS,
    HEADERS,
    RESET,
    SEARCH_DETAILS_MORE_RESULTS,
    SEARCH_DETAILS_ONE_RESULT,
)
from tests.mocks.raw import (
    COMBINATION_PARAMS,
    HTTP_200,
    KEYWORDS,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_SEARCH,
)

LOG_QUOTA = fqn(KeywordCombinationFinder, "LOG.quota")
SURVEY_DETAIL = SurveyDetail()
GET = fqn(RetryClient.get)


@mark.asyncio
async def test_combination_details(mocker: Mocker, client: Client):
    spy_quota = mocker.spy(SurveyDetail, "set_quota_data")
    spy_log = mocker.patch(LOG_QUOTA)
    mocker.patch(GET, new=AsyncMock(side_effect=COMBINATION_DETAILS))

    COMBINATION_PARAMS.update({"keywords": KEYWORDS[:2]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    bundle: ResponseBundle = spy_quota.call_args_list[0].args[1]

    spy_quota.assert_called_once()
    spy_log.assert_called_once()

    assert res.status_code == spy_log.call_args_list[0].args[1] == HTTP_200
    assert isinstance(spy_log.call_args_list[0].args[0], ScopusHeaders)
    assert bundle.headers == HEADERS

    assert res.headers["X-Limit"] == "20000"
    assert res.headers["X-Remaining"] == "12345"
    assert res.headers["X-Reset"] == str(RESET)
    assert res.headers["X-ELS-Status"] == "OK"


@mark.asyncio
async def test_search_details_one_result(mocker: Mocker, client: Client):
    spy_search = mocker.spy(SurveyDetail, "set_search_data")
    spy_quota = mocker.spy(SurveyDetail, "set_quota_data")
    spy_loss = mocker.spy(SurveyDetail, "set_loss")
    spy_log = mocker.patch(LOG_QUOTA)
    mocker.patch(GET, new=AsyncMock(side_effect=SEARCH_DETAILS_ONE_RESULT))

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    bundle: ResponseBundle = spy_quota.call_args_list[0].args[1]
    loss: float = spy_loss.call_args_list[0].args[1]

    spy_search.assert_called_once()
    spy_quota.assert_called_once()
    spy_loss.assert_called_once()
    spy_log.assert_called_once()

    assert res.status_code == spy_log.call_args_list[0].args[1] == HTTP_200
    assert isinstance(spy_log.call_args_list[0].args[0], ScopusHeaders)
    assert isinstance(spy_search.call_args_list[0].args[1], ScopusSearch)
    assert bundle.headers == HEADERS and loss == 0.0

    assert res.headers["X-Total"] == "1"
    assert res.headers["X-Items-Per-Page"] == "1"
    assert res.headers["X-Pages-Count"] == "1"
    assert res.headers["X-Limit"] == "20000"
    assert res.headers["X-Remaining"] == "12345"
    assert res.headers["X-Reset"] == str(RESET)
    assert res.headers["X-ELS-Status"] == "OK"
    assert res.headers["X-Loss"] == "0.00%"


@mark.asyncio
async def test_search_details_more_results(mocker: Mocker, client: Client):
    spy_search = mocker.spy(SurveyDetail, "set_search_data")
    spy_quota = mocker.spy(SurveyDetail, "set_quota_data")
    spy_loss = mocker.spy(SurveyDetail, "set_loss")
    spy_log = mocker.patch(LOG_QUOTA)
    mocker.patch(GET, new=AsyncMock(side_effect=SEARCH_DETAILS_MORE_RESULTS))

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    bundle: ResponseBundle = spy_quota.call_args_list[0].args[1]
    loss: float = spy_loss.call_args_list[0].args[1]

    spy_search.assert_called_once()
    spy_quota.assert_called_once()
    spy_loss.assert_called_once()
    spy_log.assert_called_once()

    assert res.status_code == spy_log.call_args_list[0].args[1] == HTTP_200
    assert isinstance(spy_log.call_args_list[0].args[0], ScopusHeaders)
    assert isinstance(spy_search.call_args_list[0].args[1], ScopusSearch)
    assert bundle.headers == HEADERS and loss == 2 / 3 * 100  # 66.6666...

    assert res.headers["X-Total"] == "3"
    assert res.headers["X-Items-Per-Page"] == "3"
    assert res.headers["X-Pages-Count"] == "1"
    assert res.headers["X-Limit"] == "20000"
    assert res.headers["X-Remaining"] == "12345"
    assert res.headers["X-Reset"] == str(RESET)
    assert res.headers["X-ELS-Status"] == "OK"
    assert res.headers["X-Loss"] == "66.67%"
