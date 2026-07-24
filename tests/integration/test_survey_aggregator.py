from httpx import AsyncClient as Client
from pandas import DataFrame
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.use_cases.similarity_filter import SimilarityFilter
from tests.mocks.helpers import get_patch, load_csv_from_response
from tests.mocks.integration import (
    EXACT_DUPLICATES,
    MORE_DIFFERENT_ARTICLES,
    ONE_DIFFERENT_ARTICLE,
    SAME_TITLE_AND_AUTHORS,
)
from tests.mocks.raw import HTTP_200, SEARCH_PARAMS, URL_SEARCH


@mark.asyncio
async def test_one_row(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(ONE_DIFFERENT_ARTICLE))
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_filter = mocker.spy(SimilarityFilter, "filter")
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    assert load_csv_from_response(res).shape[0] == 1
    assert res.status_code == HTTP_200 and mock.call_count == 2
    spy_drop.assert_not_called()
    spy_filter.assert_not_called()


@mark.asyncio
async def test_more_rows(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(MORE_DIFFERENT_ARTICLES))
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_filter = mocker.spy(SimilarityFilter, "filter")
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    assert load_csv_from_response(res).shape[0] == 7
    assert res.status_code == HTTP_200 and mock.call_count == 8
    spy_drop.assert_called()
    spy_filter.assert_called()


@mark.asyncio
async def test_drop_exact_duplicates(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(EXACT_DUPLICATES))
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_reset = mocker.spy(DataFrame, "reset_index")
    spy_filter = mocker.spy(SimilarityFilter, "filter")

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    df = load_csv_from_response(res)
    df_in: DataFrame = spy_drop.call_args_list[0].args[0]
    df_out: DataFrame = spy_reset.call_args_list[0].args[0]

    assert res.status_code == HTTP_200 and mock.call_count == 3
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1
    assert df.shape[0] == 1
    spy_drop.assert_called()
    spy_filter.assert_not_called()


@mark.asyncio
async def test_drop_same_title_and_authors(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(SAME_TITLE_AND_AUTHORS))
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_reset = mocker.spy(DataFrame, "reset_index")
    spy_filter = mocker.spy(SimilarityFilter, "filter")

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    df = load_csv_from_response(res)
    df_in: DataFrame = spy_drop.call_args_list[1].args[0]
    df_out: DataFrame = spy_reset.call_args_list[1].args[0]

    assert res.status_code == HTTP_200 and mock.call_count == 3
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1
    assert df.shape[0] == 1
    spy_drop.assert_called()
    spy_filter.assert_not_called()


@mark.asyncio
async def test_non_ratio(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(MORE_DIFFERENT_ARTICLES))
    spy_filter = mocker.spy(SimilarityFilter, "filter")

    mocker.patch.dict(SEARCH_PARAMS, {"ratio": 0})
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    df = load_csv_from_response(res)

    assert res.status_code == HTTP_200 and mock.call_count == 8
    assert df.shape[0] == 7
    spy_filter.assert_not_called()
