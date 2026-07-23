# mypy: disable-error-code="index"
import asyncio

from httpx import AsyncClient as Client
from pydantic import ValidationError
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.adapters.gateway.scopus_search_api import ScopusVolumeScouter
from src.adapters.helpers.response_auditor import validate_search_response
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import HTTPError
from tests.conftest import assert_error_json
from tests.mocks.errors import HTTP_ERROR, PYDANTIC_VALIDATION_ERROR
from tests.mocks.helpers import fqn, get_patch, response_mock
from tests.mocks.raw import (
    COMBINATION_PARAMS,
    HTTP_502,
    KEYWORDS,
    RAW_SEARCH_OK,
    URL_COMBINATION,
)


VALIDATE = fqn(ScopusVolumeScouter, validate_search_response)
# CHAIN = fqn(SurveyCombinations, itertools.chain, "itertools")


@mark.asyncio
async def test_fetch_multiple_task_error(mocker: Mocker, client: Client):
    spy = mocker.patch(VALIDATE, wraps=validate_search_response)
    mock = mocker.patch(
        *get_patch(
            [
                response_mock(RAW_SEARCH_OK),
                response_mock(RAW_SEARCH_OK),
                response_mock(RAW_SEARCH_OK),
                KeyError("any"),
            ]
        )
    )
    mocker.patch.dict(COMBINATION_PARAMS, {"keywords": KEYWORDS[:3]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    details = assert_error_json(res, HTTP_502, ExcMsg.REQUEST_EXCEPTION)
    assert mock.call_count == 7 and 4 > spy.call_count > 1
    assert details[0]["type"] == fqn(KeyError)
    assert details[0]["message"] == "any"


@mark.asyncio
async def test_fetch_multiple_http_error(mocker: Mocker, client: Client):
    spy = mocker.patch(VALIDATE, wraps=validate_search_response)
    mock = mocker.patch(
        *get_patch(
            [
                response_mock(RAW_SEARCH_OK),
                response_mock(RAW_SEARCH_OK),
                response_mock(RAW_SEARCH_OK),
                HTTP_ERROR,
            ]
        )
    )
    mocker.patch.dict(COMBINATION_PARAMS, {"keywords": KEYWORDS[:3]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    details = assert_error_json(res, HTTP_502, ExcMsg.REQUEST_EXCEPTION)
    assert mock.call_count == 7 and 4 > spy.call_count > 1
    assert details[0]["type"] == fqn(HTTPError)
    assert details[0]["message"] == ExcMsg.INTERNAL_ERROR


@mark.asyncio
async def test_fetch_multiple_cancelled_error(mocker: Mocker, client: Client):
    spy = mocker.patch(VALIDATE, wraps=validate_search_response)
    mock = mocker.patch(
        *get_patch(
            [
                response_mock(RAW_SEARCH_OK),
                response_mock(RAW_SEARCH_OK),
                response_mock(RAW_SEARCH_OK),
                asyncio.CancelledError("any"),
            ]
        )
    )
    mocker.patch.dict(COMBINATION_PARAMS, {"keywords": KEYWORDS[:3]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    details = assert_error_json(res, HTTP_502, ExcMsg.REQUEST_EXCEPTION)
    # TaskGroup swallows CancelledError
    assert mock.call_count == 7 and 4 > spy.call_count > 1
    assert details[0]["type"] == fqn(StopAsyncIteration)
    assert details[0]["message"]
    assert details[0]["cause"]["type"] == fqn(StopIteration)


@mark.asyncio
async def test_fetch_multiple_common_error(mocker: Mocker, client: Client):
    spy = mocker.patch(VALIDATE, wraps=validate_search_response)
    mock = mocker.patch(
        *get_patch(
            [
                response_mock(RAW_SEARCH_OK),
                response_mock(RAW_SEARCH_OK),
                response_mock(RAW_SEARCH_OK),
                PYDANTIC_VALIDATION_ERROR,
            ]
        )
    )
    mocker.patch.dict(COMBINATION_PARAMS, {"keywords": KEYWORDS[:3]})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    details = assert_error_json(res, HTTP_502, ExcMsg.REQUEST_EXCEPTION)
    assert mock.call_count == 7 and 4 > spy.call_count > 1
    assert details[0]["type"] == fqn(ValidationError)
    assert details[0]["message"] == "Field required"
    assert details[0]["errors"][0]["type"] == "missing"
