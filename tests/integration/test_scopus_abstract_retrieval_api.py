# mypy: disable-error-code="index"
from asyncio import CancelledError
from unittest.mock import AsyncMock

from aiohttp_retry import RetryClient
from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.common.error_messages import CANCELLED_ERROR
from src.core.data.enums import Column
from src.utils.progress_bar import ProgressBar
from tests.conftest import assert_error_json
from tests.mocks.helpers import fqn, load_csv_file_response_dataframe
from tests.mocks.integration import (
    RETRIEVE_CANCELLED_ERROR,
    RETRIEVE_MORE_ABSTRACTS,
    RETRIEVE_ONE_ABSTRACT_AUTHORS,
    RETRIEVE_ONE_ABSTRACT_FULL,
    RETRIEVE_ONE_PARTIAL_ABSTRACT,
    RETRIEVE_TWO_ABSTRACTS,
)
from tests.mocks.raw import HTTP_200, HTTP_503, SEARCH_PARAMS, URL_SEARCH

STEP = fqn(ProgressBar.step)
GET = fqn(RetryClient.get)


@mark.asyncio
async def test_retrieve_one_partial_abstract(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=RETRIEVE_ONE_PARTIAL_ABSTRACT),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 2
    df = load_csv_file_response_dataframe(res)
    assert df.shape[0] == 2  # +1 footnote
    assert df[Column.AUTHORS].iloc[0] == "any_author"


@mark.asyncio
async def test_retrieve_one_abstract_authors(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=RETRIEVE_ONE_ABSTRACT_AUTHORS),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 2
    df = load_csv_file_response_dataframe(res)
    assert df.shape[0] == 2  # +1 footnote
    assert df[Column.AUTHORS].iloc[0] == "any_author_1, any_author_2"


@mark.asyncio
async def test_retrieve_one_abstract_full(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=RETRIEVE_ONE_ABSTRACT_FULL),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 2
    df = load_csv_file_response_dataframe(res)
    assert df.shape[0] == 2  # +1 footnote
    assert df["Abstract"].iloc[0] == "any_abstract"


@mark.asyncio
async def test_retrieve_two_abstracts(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=RETRIEVE_TWO_ABSTRACTS),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3
    df = load_csv_file_response_dataframe(res)
    assert df.shape[0] == 2  # +1 footnote


@mark.asyncio
async def test_retrieve_more_abstracts(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=RETRIEVE_MORE_ABSTRACTS),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 26
    df = load_csv_file_response_dataframe(res)
    assert df.shape[0] == 2  # +1 footnote


@mark.asyncio
async def test_retrieve_cancelled_error(mocker: Mocker, client: Client):
    mocker.patch(STEP, side_effect=[None, None, None, CancelledError("any")])
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=RETRIEVE_CANCELLED_ERROR),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    errors = assert_error_json(res, HTTP_503, CANCELLED_ERROR)
    assert errors[0]["type"] == fqn(CancelledError)
    assert errors[0]["detail"] == "any" and mock.call_count == 8
