# mypy: disable-error-code="index"
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.common.types import ResponseBundle
from src.core.config.scopus import BOOLEAN_OPERATOR
from src.core.data.csv_builder import write_csv_file
from src.core.data.serializers import ScopusHeaders, ScopusPage
from src.core.data.survey_details import SurveyDetails
from src.core.use_cases.keyword_scouter import KeywordsScouter
from src.core.use_cases.survey_orchestrator import SurveyOrchestrator
from src.utils import logger
from tests.mocks.helpers import fqn, get_patch, spec
from tests.mocks.integration import (
    COMBINATION_DETAILS,
    HEADERS,
    RESET_DATETIME,
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


LOG_QUOTA = spec(KeywordsScouter, logger.quota, "logger")
WRITE_CSV = fqn(SurveyOrchestrator, write_csv_file)


@mark.asyncio
async def test_combination_details(mocker: Mocker, client: Client):
    spy_quota = mocker.spy(SurveyDetails, "set_search_quota")
    spy_log = mocker.patch(**LOG_QUOTA)
    mocker.patch(*get_patch(COMBINATION_DETAILS))

    mocker.patch.dict(COMBINATION_PARAMS, {"keywords": KEYWORDS[:2]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    bundle: ResponseBundle = spy_quota.call_args_list[0].args[1]

    spy_quota.assert_called_once()
    spy_log.assert_called_once()

    assert res.status_code == spy_log.call_args_list[0].args[1] == HTTP_200
    assert isinstance(spy_log.call_args_list[0].args[0], ScopusHeaders)
    assert bundle.headers == HEADERS

    assert res.headers["X-Keywords"] == BOOLEAN_OPERATOR.join(KEYWORDS[:2])
    assert res.headers["X-Search-Limit"] == "20000"
    assert res.headers["X-Search-Remaining"] == "12345"
    assert res.headers["X-Search-Reset"] == RESET_DATETIME


@mark.asyncio
async def test_search_details_one_result(mocker: Mocker, client: Client):
    spy_search = mocker.spy(SurveyDetails, "set_search_data")
    spy_search_quota = mocker.spy(SurveyDetails, "set_search_quota")
    spy_abstract_quota = mocker.spy(SurveyDetails, "set_abstract_quota")
    spy_loss = mocker.spy(SurveyDetails, "set_loss")
    spy_write = mocker.patch(WRITE_CSV, wraps=write_csv_file)
    spy_log = mocker.patch(**LOG_QUOTA)
    mocker.patch(*get_patch(SEARCH_DETAILS_ONE_RESULT))

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    search_bundle: ResponseBundle = spy_search_quota.call_args_list[0].args[1]
    abstract_bundle: ResponseBundle = spy_abstract_quota.call_args_list[
        0
    ].args[1]
    loss: float = spy_loss.call_args_list[0].args[1]
    metadata: list[str] = spy_write.call_args_list[0].args[2]

    spy_search.assert_called_once()
    spy_search_quota.assert_called_once()
    spy_abstract_quota.assert_called_once()
    spy_loss.assert_called_once()
    spy_log.assert_called()

    assert res.status_code == spy_log.call_args_list[0].args[1] == HTTP_200
    assert isinstance(spy_log.call_args_list[0].args[0], ScopusHeaders)
    assert isinstance(spy_search.call_args_list[0].args[1], ScopusPage)
    assert search_bundle.headers == abstract_bundle.headers == HEADERS
    assert loss == 0.0

    assert metadata[0] == "total=1" and metadata[1] == "items_per_page=1"
    assert metadata[2] == "pages_count=1"
    assert metadata[3] == "results=1doc / 1doc"
    assert metadata[4] == "loss=0doc / 0.00%"

    assert res.headers["X-Combination"] == KEYWORDS[0]
    assert res.headers["X-Total"] == "1"
    assert res.headers["X-Items-Per-Page"] == "1"
    assert res.headers["X-Pages-Count"] == "1"
    assert res.headers["X-Search-Limit"] == "20000"
    assert res.headers["X-Search-Remaining"] == "12345"
    assert res.headers["X-Search-Reset"] == RESET_DATETIME
    assert res.headers["X-Abstract-Limit"] == "20000"
    assert res.headers["X-Abstract-Remaining"] == "12345"
    assert res.headers["X-Abstract-Reset"] == RESET_DATETIME
    assert res.headers["X-Results"] == "1doc / 1doc"
    assert res.headers["X-Loss"] == "0doc / 0.00%"


@mark.asyncio
async def test_search_details_more_results(mocker: Mocker, client: Client):
    spy_search = mocker.spy(SurveyDetails, "set_search_data")
    spy_search_quota = mocker.spy(SurveyDetails, "set_search_quota")
    spy_abstract_quota = mocker.spy(SurveyDetails, "set_abstract_quota")
    spy_loss = mocker.spy(SurveyDetails, "set_loss")
    spy_write = mocker.patch(WRITE_CSV, wraps=write_csv_file)
    spy_log = mocker.patch(**LOG_QUOTA)
    mocker.patch(*get_patch(SEARCH_DETAILS_MORE_RESULTS))

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    search_bundle: ResponseBundle = spy_search_quota.call_args_list[0].args[1]
    abstract_bundle: ResponseBundle = spy_abstract_quota.call_args_list[
        0
    ].args[1]
    loss: float = spy_loss.call_args_list[0].args[1]
    metadata: list[str] = spy_write.call_args_list[0].args[2]

    spy_search.assert_called_once()
    spy_search_quota.assert_called_once()
    assert spy_abstract_quota.call_count == 2
    spy_loss.assert_called_once()
    spy_log.assert_called()

    assert res.status_code == spy_log.call_args_list[0].args[1] == HTTP_200
    assert isinstance(spy_log.call_args_list[0].args[0], ScopusHeaders)
    assert isinstance(spy_search.call_args_list[0].args[1], ScopusPage)
    assert search_bundle.headers == abstract_bundle.headers == HEADERS
    assert loss == 2

    assert metadata[0] == "total=3" and metadata[1] == "items_per_page=3"
    assert metadata[2] == "pages_count=1"
    assert metadata[3] == "results=3doc / 3doc"
    assert metadata[4] == "loss=2doc / 66.67%"

    assert res.headers["X-Combination"] == KEYWORDS[0]
    assert res.headers["X-Total"] == "3"
    assert res.headers["X-Items-Per-Page"] == "3"
    assert res.headers["X-Pages-Count"] == "1"
    assert res.headers["X-Search-Limit"] == "20000"
    assert res.headers["X-Search-Remaining"] == "12345"
    assert res.headers["X-Search-Reset"] == RESET_DATETIME
    assert res.headers["X-Abstract-Limit"] == "20000"
    assert res.headers["X-Abstract-Remaining"] == "12345"
    assert res.headers["X-Abstract-Reset"] == RESET_DATETIME
    assert res.headers["X-Results"] == "3doc / 3doc"
    assert res.headers["X-Loss"] == "2doc / 66.67%"
