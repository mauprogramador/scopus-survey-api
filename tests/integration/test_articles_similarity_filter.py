# mypy: disable-error-code="index"
from concurrent.futures import CancelledError
from datetime import datetime

from httpx import AsyncClient as Client
from pandas import DataFrame, Series, isna, to_datetime
from pandas.api.typing import DataFrameGroupBy
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.data.enums import Column, ExcMsg
from src.core.use_cases.articles_similarity_filter import (
    ArticlesSimilarityFilter,
)
from tests.conftest import assert_error_json
from tests.mocks.helpers import Patch, fqn, get_patch, load_csv_from_response
from tests.mocks.integration import (
    MORE_GROUPS_MORE_SIMILAR,
    MORE_GROUPS_NO_SIMILAR,
    MORE_GROUPS_TWO_SIMILAR,
    NO_DATETIME_LEFT,
    NO_REPEATED_AUTHORS,
    ONE_DATETIME_LEFT,
    ONE_GROUP_MORE_SIMILAR,
    ONE_GROUP_NO_SIMILAR,
    ONE_GROUP_TWO_SIMILAR,
)
from tests.mocks.raw import (
    HTTP_200,
    HTTP_503,
    LOGGER_MOCK,
    SEARCH_PARAMS,
    URL_SEARCH,
)


TO_DATETIME = fqn(ArticlesSimilarityFilter, to_datetime)
LOG_DEBUG = Patch(ArticlesSimilarityFilter, LOGGER_MOCK.debug)
IDXMAX = Patch(Series.idxmax)


@mark.asyncio
async def test_one_group_two_similar_titles(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(ONE_GROUP_TWO_SIMILAR))
    spy = mocker.spy(ArticlesSimilarityFilter, "_get_single_group_index")
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    spy.assert_called_once()

    assert res.status_code == HTTP_200 and mock.call_count == 3
    df = load_csv_from_response(res)
    assert df.shape[0] == 1
    assert df[Column.AUTHORS].iloc[0] == "a"
    assert df[Column.DATE].iloc[0] == "2025-06-02"


@mark.asyncio
async def test_one_group_more_similar_titles(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(ONE_GROUP_MORE_SIMILAR))
    spy = mocker.spy(ArticlesSimilarityFilter, "_get_single_group_index")
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    spy.assert_called_once()

    assert res.status_code == HTTP_200 and mock.call_count == 6
    df = load_csv_from_response(res)
    assert df.shape[0] == 1
    assert df[Column.AUTHORS].iloc[0] == "a"
    assert df[Column.DATE].iloc[0] == "2025-06-05"


@mark.asyncio
async def test_one_group_no_similar_titles(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(ONE_GROUP_NO_SIMILAR))
    spy = mocker.spy(ArticlesSimilarityFilter, "_get_single_group_index")
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    spy.assert_called_once()
    assert res.status_code == HTTP_200 and mock.call_count == 3
    df = load_csv_from_response(res)
    assert df.shape[0] == 2


@mark.asyncio
async def test_more_groups_two_similar_titles(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(MORE_GROUPS_TWO_SIMILAR))
    spy = mocker.spy(ArticlesSimilarityFilter, "_get_single_group_index")
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    spy.assert_not_called()

    assert res.status_code == HTTP_200 and mock.call_count == 6
    df = load_csv_from_response(res)
    assert df.shape[0] == 3
    assert df[Column.AUTHORS].tolist() == ["a", "b", "c"]
    recent_dates = ["2025-06-05", "2025-06-05", "2025-06-01"]
    assert df[Column.DATE].tolist() == recent_dates


@mark.asyncio
async def test_more_groups_more_similar_titles(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(MORE_GROUPS_MORE_SIMILAR))
    spy = mocker.spy(ArticlesSimilarityFilter, "_get_single_group_index")
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    spy.assert_not_called()

    assert res.status_code == HTTP_200 and mock.call_count == 10
    df = load_csv_from_response(res)
    assert df.shape[0] == 3
    assert df[Column.AUTHORS].tolist() == ["a", "b", "c"]
    recent_dates = ["2025-06-04", "2025-06-03", "2025-06-02"]
    assert df[Column.DATE].tolist() == recent_dates


@mark.asyncio
async def test_more_groups_no_similar_titles(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(MORE_GROUPS_NO_SIMILAR))
    spy = mocker.spy(ArticlesSimilarityFilter, "_get_single_group_index")
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    spy.assert_not_called()

    assert res.status_code == HTTP_200 and mock.call_count == 10
    df = load_csv_from_response(res)
    assert df.shape[0] == 9


@mark.asyncio
async def test_to_datetime_no_left(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(NO_DATETIME_LEFT))
    spy_to_datetime = mocker.patch(TO_DATETIME, wraps=to_datetime)
    spy_dropna = mocker.spy(DataFrame, "dropna")
    spy_log_debug = mocker.patch(**LOG_DEBUG)

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    df_to_datetime: Series = spy_to_datetime.call_args_list[0].args[0]
    df_dropna: DataFrame = spy_dropna.call_args_list[0].args[0]

    spy_log_debug.assert_called_with({"invalids_datetime": 0})
    spy_to_datetime.assert_called_once()
    spy_dropna.assert_called_once()

    assert res.status_code == HTTP_200 and mock.call_count == 3
    df = load_csv_from_response(res)
    assert df.shape[0] == 2

    assert all(isinstance(value, str) for value in df_to_datetime)
    assert all(isna(value) for value in df_dropna[Column.DATE])


@mark.asyncio
async def test_to_datetime_one_left(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(ONE_DATETIME_LEFT))
    spy_to_datetime = mocker.patch(TO_DATETIME, wraps=to_datetime)
    spy_dropna = mocker.spy(DataFrame, "dropna")
    spy_log_debug = mocker.patch(**LOG_DEBUG)

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    df_to_datetime: DataFrame = spy_to_datetime.call_args_list[0].args[0]
    df_dropna: DataFrame = spy_dropna.call_args_list[0].args[0]

    spy_log_debug.assert_called_with({"invalids_datetime": 1})
    spy_to_datetime.assert_called_once()
    spy_dropna.assert_called_once()

    assert res.status_code == HTTP_200 and mock.call_count == 3
    df = load_csv_from_response(res)
    assert df.shape[0] == 2

    assert all(isinstance(value, str) for value in df_to_datetime)
    assert isinstance(df_dropna[Column.DATE].iloc[0], datetime)
    assert isna(df_dropna[Column.DATE].iloc[1])


@mark.asyncio
async def test_no_repeated_authors(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(NO_REPEATED_AUTHORS))
    spy_dropna = mocker.spy(DataFrame, "dropna")
    spy_filter = mocker.spy(DataFrameGroupBy, "filter")
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    spy_dropna.assert_called_once()
    spy_filter.assert_not_called()

    assert res.status_code == HTTP_200 and mock.call_count == 3
    df = load_csv_from_response(res)
    assert df.shape[0] == 2


@mark.asyncio
async def test_filter_drop_singles(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(MORE_GROUPS_TWO_SIMILAR))
    spy_filter = mocker.spy(DataFrameGroupBy, "filter")
    spy_groupby = mocker.spy(DataFrame, "groupby")

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    df_group: DataFrameGroupBy = spy_filter.call_args_list[0].args[0]
    df_drop: DataFrame = spy_groupby.call_args_list[1].args[0]

    assert res.status_code == HTTP_200 and mock.call_count == 6
    df = load_csv_from_response(res)
    assert df.shape[0] == 3
    assert df_group.ngroups == 3 and df_drop.shape[0] == 4


@mark.asyncio
async def test_discard_one_older_similar(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(ONE_GROUP_TWO_SIMILAR))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3
    df = load_csv_from_response(res)
    assert df.shape[0] == 1
    assert df[Column.DATE].iloc[0] == "2025-06-02"


@mark.asyncio
async def test_discard_all_older_similar(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(ONE_GROUP_MORE_SIMILAR))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 6
    df = load_csv_from_response(res)
    assert df.shape[0] == 1
    assert df[Column.DATE].iloc[0] == "2025-06-05"


@mark.asyncio
async def test_cancelled_error(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(MORE_GROUPS_MORE_SIMILAR))
    mocker.patch(**IDXMAX([1, CancelledError("any")]))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert mock.call_count == 10
    errors = assert_error_json(res, HTTP_503, ExcMsg.CANCELLED_ERROR)
    assert errors[0]["type"] == fqn(CancelledError)
    assert errors[0]["detail"] == "any"


@mark.asyncio
async def test_drop_similar(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(ONE_GROUP_MORE_SIMILAR))
    spy_drop = mocker.spy(DataFrame, "drop")

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    df_in: DataFrame = spy_drop.call_args_list[0].args[0]
    similar_titles: set = spy_drop.call_args_list[0].args[1]

    assert res.status_code == HTTP_200 and mock.call_count == 6
    df = load_csv_from_response(res)
    assert df.shape[0] == 1
    assert len(similar_titles) == 4 and df_in.shape[0] == 5
