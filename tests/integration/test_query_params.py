from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.data.enums import Button
from src.core.domain.factory import make_aggregator, make_combinator
from src.core.use_cases.keyword_scouter import KeywordsScouter
from src.core.use_cases.survey_orchestrator import SurveyOrchestrator
from src.framework.fastapi.routes import survey_bibliographic_data
from tests.conftest import assert_error_json
from tests.mocks.errors import REQUEST_VALIDATION_ERROR
from tests.mocks.helpers import (
    Patch,
    mock_retrieve_articles,
    mock_survey_combinations,
    trans,
)
from tests.mocks.raw import (
    API_KEY,
    COMBINATION_PARAMS,
    CSV_PARAMS,
    HTTP_200,
    HTTP_422,
    KEYWORDS,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_CSV,
    URL_SEARCH,
)


MAKE_COMBINATOR = Patch(survey_bibliographic_data, make_combinator)
MAKE_AGGREGATOR = Patch(survey_bibliographic_data, make_aggregator)
SURVEY_COMBINATIONS = MagicMock(
    KeywordsScouter,
    survey_combinations=AsyncMock(
        KeywordsScouter.survey_combinations,
        side_effect=mock_survey_combinations,
    ),
)
RETRIEVE_ARTICLES = MagicMock(
    SurveyOrchestrator,
    retrieve_articles=AsyncMock(
        SurveyOrchestrator.retrieve_articles,
        side_effect=mock_retrieve_articles,
    ),
)


@mark.asyncio
async def test_csv_params_valid_data(client: Client):
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_csv_params_raise_errors(client: Client):
    res = await client.get(URL_CSV)
    details = assert_error_json(res, HTTP_422, trans(REQUEST_VALIDATION_ERROR))
    assert len(details) == 3


@mark.asyncio
async def test_combination_params_valid_data(mocker: Mocker, client: Client):
    mocker.patch(**MAKE_COMBINATOR(SURVEY_COMBINATIONS))
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_combination_params_overridden_default(
    mocker: Mocker, client: Client
):
    mocker.patch(**MAKE_COMBINATOR(SURVEY_COMBINATIONS))
    params = {
        "apiKey": API_KEY,
        "startYear": "2020",
        "endYear": "2021",
        "docType": "ar",
        "pubStage": "final",
        "language": "english",
        "openAccess": "0",
        "srcType": "j",
        "subjArea": "COMP",
        "page_range": "0-4",
        "keywords": KEYWORDS,
        "button": Button.COMBINATION.value,
    }
    res = await client.get(URL_COMBINATION, params=params)
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_combination_params_raise_errors(client: Client):
    res = await client.get(URL_COMBINATION)
    details = assert_error_json(res, HTTP_422, trans(REQUEST_VALIDATION_ERROR))
    assert len(details) == 4


@mark.asyncio
async def test_combination_params_empty_to_default(
    mocker: Mocker, client: Client
):
    mocker.patch(**MAKE_COMBINATOR(SURVEY_COMBINATIONS))
    params = {
        "apiKey": API_KEY,
        "docType": "",
        "pubStage": " ",
        "keywords": KEYWORDS,
        "button": Button.COMBINATION.value,
    }
    res = await client.get(URL_COMBINATION, params=params)
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_combination_params_keywords(mocker: Mocker, client: Client):
    mocker.patch(**MAKE_COMBINATOR(SURVEY_COMBINATIONS))
    params = {
        "apiKey": API_KEY,
        "keywords": ["any,any"],
        "button": Button.COMBINATION.value,
    }

    res = await client.get(URL_COMBINATION, params=params)
    assert res.status_code == HTTP_200

    params.update({"keywords": ["any,any,any,any,any"]})
    res = await client.get(URL_COMBINATION, params=params)
    assert res.status_code == HTTP_422

    params.update({"keywords": ["any"]})
    res = await client.get(URL_COMBINATION, params=params)
    assert res.status_code == HTTP_422


@mark.asyncio
async def test_search_params_valid_data(mocker: Mocker, client: Client):
    mocker.patch(**MAKE_AGGREGATOR(RETRIEVE_ARTICLES))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_search_params_overridden_default(
    mocker: Mocker, client: Client
):
    mocker.patch(**MAKE_AGGREGATOR(RETRIEVE_ARTICLES))
    params = {
        "apiKey": API_KEY,
        "keywords": KEYWORDS,
        "combination": "Python AND Web",
        "ratio": "25",
        "button": Button.SURVEY.value,
    }
    res = await client.get(URL_SEARCH, params=params)
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_search_params_raise_errors(mocker: Mocker, client: Client):
    mocker.patch(**MAKE_AGGREGATOR(RETRIEVE_ARTICLES))
    res = await client.get(URL_SEARCH)
    details = assert_error_json(res, HTTP_422, trans(REQUEST_VALIDATION_ERROR))
    assert len(details) == 5


@mark.asyncio
async def test_search_params_empty_to_default(mocker: Mocker, client: Client):
    mocker.patch(**MAKE_AGGREGATOR(RETRIEVE_ARTICLES))
    params = {
        "apiKey": API_KEY,
        "docType": "",
        "pubStage": " ",
        "keywords": KEYWORDS,
        "combination": "Python",
        "button": Button.SURVEY.value,
    }
    res = await client.get(URL_SEARCH, params=params)
    assert res.status_code == HTTP_200
