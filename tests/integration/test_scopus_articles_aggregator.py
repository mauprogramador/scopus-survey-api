from unittest.mock import ANY, AsyncMock

from aiohttp_retry import RetryClient
from httpx import AsyncClient as Client
from pandas import DataFrame
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.config.scopus import FOOTNOTE
from src.core.data.survey_details import SurveyDetails
from src.core.use_cases.articles_similarity_filter import (
    ArticlesSimilarityFilter,
)
from tests.mocks.helpers import fqn, load_csv_file_response_dataframe
from tests.mocks.integration import (
    EXACT_DUPLICATES,
    MORE_DIFFERENT_ARTICLES,
    ONE_DIFFERENT_ARTICLE,
    SAME_TITLE_AND_AUTHORS,
)
from tests.mocks.raw import HTTP_200, SEARCH_PARAMS, URL_SEARCH

GET = fqn(RetryClient.get)


@mark.asyncio
async def test_one_row(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=ONE_DIFFERENT_ARTICLE),
    )
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_filter = mocker.spy(ArticlesSimilarityFilter, "filter")
    spy_loss = mocker.spy(SurveyDetails, "set_loss")
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    df = load_csv_file_response_dataframe(res)
    assert res.status_code == HTTP_200 and mock.call_count == 2
    assert df.shape == (2, 11)  # +1 footnote
    spy_drop.assert_not_called()
    spy_filter.assert_not_called()
    spy_loss.assert_called_once_with(ANY, 0, 0.0)


@mark.asyncio
async def test_more_rows(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=MORE_DIFFERENT_ARTICLES),
    )
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_filter = mocker.spy(ArticlesSimilarityFilter, "filter")
    spy_loss = mocker.spy(SurveyDetails, "set_loss")
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    df = load_csv_file_response_dataframe(res)
    assert res.status_code == HTTP_200 and mock.call_count == 8
    assert df.shape == (8, 11)  # +1 footnote
    spy_drop.assert_called()
    spy_filter.assert_called()
    spy_loss.assert_called_once_with(ANY, 0, 0.0)


@mark.asyncio
async def test_drop_exact_duplicates(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=EXACT_DUPLICATES),
    )
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_reset = mocker.spy(DataFrame, "reset_index")
    spy_filter = mocker.spy(ArticlesSimilarityFilter, "filter")
    spy_loss = mocker.spy(SurveyDetails, "set_loss")

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    df = load_csv_file_response_dataframe(res)
    df_in: DataFrame = spy_drop.call_args_list[0].args[0]
    df_out: DataFrame = spy_reset.call_args_list[0].args[0]

    assert res.status_code == HTTP_200 and mock.call_count == 3
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1
    assert df.shape == (2, 11)  # +1 footnote
    spy_drop.assert_called()
    spy_filter.assert_not_called()
    spy_loss.assert_called_once_with(ANY, 1, 50.0)


@mark.asyncio
async def test_drop_same_title_and_authors(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=SAME_TITLE_AND_AUTHORS),
    )
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_reset = mocker.spy(DataFrame, "reset_index")
    spy_filter = mocker.spy(ArticlesSimilarityFilter, "filter")
    spy_loss = mocker.spy(SurveyDetails, "set_loss")

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    df = load_csv_file_response_dataframe(res)
    df_in: DataFrame = spy_drop.call_args_list[1].args[0]
    df_out: DataFrame = spy_reset.call_args_list[1].args[0]

    assert res.status_code == HTTP_200 and mock.call_count == 3
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1
    assert df.shape == (2, 11)  # +1 footnote
    spy_drop.assert_called()
    spy_filter.assert_not_called()
    spy_loss.assert_called_once_with(ANY, 1, 50.0)


@mark.asyncio
async def test_non_ratio(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=MORE_DIFFERENT_ARTICLES),
    )
    spy_filter = mocker.spy(ArticlesSimilarityFilter, "filter")

    SEARCH_PARAMS.setdefault("threshold", 0)
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    df = load_csv_file_response_dataframe(res)

    assert res.status_code == HTTP_200 and mock.call_count == 8
    assert df.shape == (8, 11)  # +1 footnote
    spy_filter.assert_not_called()


@mark.asyncio
async def test_footnote(mocker: Mocker, client: Client):
    mock = mocker.patch(
        GET,
        new=AsyncMock(side_effect=EXACT_DUPLICATES),
    )
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    df = load_csv_file_response_dataframe(res)

    assert res.status_code == HTTP_200 and mock.call_count == 3
    assert df.shape == (2, 11)  # +1 footnote
    assert df.iloc[-1].iloc[0].startswith(FOOTNOTE[:41])
    assert df.iloc[-1].iloc[0].endswith(FOOTNOTE[-50:])
