# mypy: disable-error-code="index"
from unittest.mock import AsyncMock, MagicMock

from fastapi.exceptions import RequestValidationError
from httpx import AsyncClient as Client
from pandas import DataFrame
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.adapters.serializers.scopus_data import ScopusAbstract, ScopusHeaders
from src.adapters.types import Button
from src.core.domain.factory import make_aggregator, make_combinator
from src.core.domain.types import Json, SurveyDetails
from src.core.use_cases.survey_aggregator import SurveyAggregator
from src.core.use_cases.survey_combinations import SurveyCombinations
from src.infra.fastapi.routes import favicon
from tests.conftest import assert_error_json
from tests.mocks.errors import REQUEST_VALIDATION_ERROR
from tests.mocks.helpers import Patch, fqn, trans
from tests.mocks.raw import (
    API_KEY,
    COMBINATION_PARAMS,
    CSV_PARAMS,
    DETAILS,
    HTTP_200,
    HTTP_422,
    KEYWORDS,
    RAW_ABSTRACT_OK,
    RAW_HEADERS_OK,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_CSV,
    URL_SEARCH,
)


MAKE_COMBINATOR = Patch(favicon, make_combinator)
MAKE_AGGREGATOR = Patch(favicon, make_aggregator)
DATASET = DataFrame([ScopusAbstract(**RAW_ABSTRACT_OK).model_dump()])


async def _mock_combinations_process(*_) -> tuple[list[Json], ScopusHeaders]:
    return [{"Any": "any"}], ScopusHeaders(**RAW_HEADERS_OK)


async def _mock_aggregator_process(*_) -> tuple[DataFrame, SurveyDetails]:
    return DATASET, DETAILS


SURVEY_COMBINATIONS = MagicMock(
    SurveyCombinations,
    process=AsyncMock(
        SurveyCombinations.process, side_effect=_mock_combinations_process
    ),
)
SURVEY_AGGREGATOR = MagicMock(
    SurveyAggregator,
    process=AsyncMock(
        SurveyAggregator.process, side_effect=_mock_aggregator_process
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
    assert details[0]["type"] == fqn(RequestValidationError)
    assert details[0]["message"] == "Field required"
    assert details[0]["errors"][0]["type"] == "missing"


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
    assert details[0]["type"] == fqn(RequestValidationError)
    assert details[0]["message"] == "Field required"
    assert len(details[0]["errors"]) == 3
    assert details[0]["errors"][0]["type"] == "missing"


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
    details = assert_error_json(res, HTTP_422, trans(REQUEST_VALIDATION_ERROR))
    assert details[0]["type"] == fqn(RequestValidationError)
    assert details[0]["errors"][0]["type"] == "too_long"

    params.update({"keywords": ["any"]})
    res = await client.get(URL_COMBINATION, params=params)
    details = assert_error_json(res, HTTP_422, trans(REQUEST_VALIDATION_ERROR))
    assert details[0]["type"] == fqn(RequestValidationError)
    assert details[0]["errors"][0]["type"] == "too_short"


@mark.asyncio
async def test_search_params_valid_data(mocker: Mocker, client: Client):
    mocker.patch(**MAKE_AGGREGATOR(SURVEY_AGGREGATOR))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200


@mark.asyncio
async def test_search_params_overridden_default(
    mocker: Mocker, client: Client
):
    mocker.patch(**MAKE_AGGREGATOR(SURVEY_AGGREGATOR))
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
    mocker.patch(**MAKE_AGGREGATOR(SURVEY_AGGREGATOR))
    res = await client.get(URL_SEARCH)
    details = assert_error_json(res, HTTP_422, trans(REQUEST_VALIDATION_ERROR))
    assert details[0]["type"] == fqn(RequestValidationError)
    assert details[0]["message"] == "Field required"
    assert len(details[0]["errors"]) == 4
    assert details[0]["errors"][0]["type"] == "missing"


@mark.asyncio
async def test_search_params_empty_to_default(mocker: Mocker, client: Client):
    mocker.patch(**MAKE_AGGREGATOR(SURVEY_AGGREGATOR))
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
