from unittest.mock import AsyncMock

from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.data.enums import Button
from src.core.domain.factory import make_aggregator, make_combinator
from src.core.use_cases.keyword_combination_finder import (
    KeywordCombinationFinder,
)
from src.core.use_cases.scopus_articles_aggregator import (
    ScopusArticlesAggregator,
)
from src.framework.fastapi.routes import survey_bibliographic_data
from tests.conftest import assert_error_json
from tests.mocks.helpers import (
    fqn,
    mock_retrieve_articles,
    mock_survey_combinations,
)
from tests.mocks.raw import (
    API_KEY,
    COMBINATION_PARAMS,
    CSRF_TOKEN,
    CSV_PARAMS,
    HTTP_200,
    HTTP_422,
    KEYWORDS,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_CSV,
    URL_SEARCH,
)

MAKE_COMBINATOR = fqn(survey_bibliographic_data, make_combinator)
MAKE_AGGREGATOR = fqn(survey_bibliographic_data, make_aggregator)
SURVEY_COMBINATIONS = AsyncMock(
    spec=KeywordCombinationFinder,
    survey_combinations=AsyncMock(side_effect=mock_survey_combinations),
)
RETRIEVE_ARTICLES = AsyncMock(
    spec=ScopusArticlesAggregator,
    retrieve_articles=AsyncMock(side_effect=mock_retrieve_articles),
)


@mark.asyncio
async def test_csv_params_valid_data(client: Client):
    res = await client.get(URL_CSV, params=CSV_PARAMS)
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_csv_params_raise_errors(client: Client):
    params = {"csrfToken": CSRF_TOKEN}
    res = await client.get(URL_CSV, params=params)
    errors = assert_error_json(res, HTTP_422, "Field required")
    assert len(errors) == 2


@mark.asyncio
async def test_combination_params_valid_data(mocker: Mocker, client: Client):
    mocker.patch(MAKE_COMBINATOR, return_value=SURVEY_COMBINATIONS)
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_combination_params_overridden_default(
    mocker: Mocker, client: Client
):
    mocker.patch(MAKE_COMBINATOR, return_value=SURVEY_COMBINATIONS)
    params = {
        "csrfToken": CSRF_TOKEN,
        "apiKey": API_KEY,
        "startYear": "2020",
        "endYear": "2021",
        "docType": "ar",
        "pubStage": "final",
        "language": "english",
        "openAccess": "0",
        "srcType": "j",
        "subjArea": "COMP",
        "pages": "short",
        "keywords": KEYWORDS,
        "button": Button.COMBINATION.value,
    }
    res = await client.get(URL_COMBINATION, params=params)
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_combination_params_raise_errors(client: Client):
    params = {"csrfToken": CSRF_TOKEN}
    res = await client.get(URL_COMBINATION, params=params)
    errors = assert_error_json(res, HTTP_422, "Field required")
    assert len(errors) == 3


@mark.asyncio
async def test_combination_params_empty_to_default(
    mocker: Mocker, client: Client
):
    mocker.patch(MAKE_COMBINATOR, return_value=SURVEY_COMBINATIONS)
    params = {
        "csrfToken": CSRF_TOKEN,
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
    mocker.patch(MAKE_COMBINATOR, return_value=SURVEY_COMBINATIONS)
    params = {
        "csrfToken": CSRF_TOKEN,
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
    mocker.patch(MAKE_AGGREGATOR, return_value=RETRIEVE_ARTICLES)
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_search_params_overridden_default(
    mocker: Mocker, client: Client
):
    mocker.patch(MAKE_AGGREGATOR, return_value=RETRIEVE_ARTICLES)
    params = {
        "csrfToken": CSRF_TOKEN,
        "apiKey": API_KEY,
        "keywords": KEYWORDS,
        "combination": "Python AND Web",
        "threshold": "25",
        "button": Button.SURVEY.value,
    }
    res = await client.get(URL_SEARCH, params=params)
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_search_params_raise_errors(mocker: Mocker, client: Client):
    mocker.patch(MAKE_AGGREGATOR, return_value=RETRIEVE_ARTICLES)
    params = {"csrfToken": CSRF_TOKEN}
    res = await client.get(URL_SEARCH, params=params)
    errors = assert_error_json(res, HTTP_422, "Field required")
    assert len(errors) == 4


@mark.asyncio
async def test_search_params_empty_to_default(mocker: Mocker, client: Client):
    mocker.patch(MAKE_AGGREGATOR, return_value=RETRIEVE_ARTICLES)
    params = {
        "csrfToken": CSRF_TOKEN,
        "apiKey": API_KEY,
        "docType": "",
        "pubStage": " ",
        "keywords": KEYWORDS,
        "combination": "Python",
        "button": Button.SURVEY.value,
    }
    res = await client.get(URL_SEARCH, params=params)
    assert res.status_code == HTTP_200
