from concurrent.futures import CancelledError, Future
from datetime import datetime

from pandas import DataFrame, Series, isna, to_datetime
from pandas.api.typing import DataFrameGroupBy
from pytest import raises
from pytest_mock import MockerFixture as Mocker

from src.core.data.enums import Column, ExcMsg
from src.core.domain.http_exceptions import ServiceUnavailable
from src.core.use_cases.articles_similarity_filter import (
    ArticlesSimilarityFilter,
)
from tests.conftest import assert_http_error
from tests.mocks.helpers import Patch, fqn
from tests.mocks.raw import HTTP_503, LOGGER_MOCK
from tests.mocks.unitary import (
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


SIMILARITY_FILTER = ArticlesSimilarityFilter()
TO_DATETIME = fqn(ArticlesSimilarityFilter, to_datetime)
LOG_DEBUG = Patch(ArticlesSimilarityFilter, LOGGER_MOCK.debug)
CANCELLED = Patch(Future.result, [None, CancelledError("any")])
RATIO = 80


def test_one_group_two_similar_titles(mocker: Mocker):
    spy = mocker.spy(ArticlesSimilarityFilter, "_get_single_group_index")
    result = SIMILARITY_FILTER.filter(ONE_GROUP_TWO_SIMILAR, RATIO)
    spy.assert_called_once()
    assert result.shape[0] == 1
    assert result[Column.AUTHORS].iloc[0] == "a"
    assert result[Column.DATE].iloc[0] == "2025-06-01"


def test_one_group_more_similar_titles(mocker: Mocker):
    spy = mocker.spy(ArticlesSimilarityFilter, "_get_single_group_index")
    result = SIMILARITY_FILTER.filter(ONE_GROUP_MORE_SIMILAR, RATIO)
    spy.assert_called_once()
    assert result.shape[0] == 1
    assert result[Column.AUTHORS].iloc[0] == "a"
    assert result[Column.DATE].iloc[0] == "2025-05-05"


def test_one_group_no_similar_titles(mocker: Mocker):
    spy = mocker.spy(ArticlesSimilarityFilter, "_get_single_group_index")
    result = SIMILARITY_FILTER.filter(ONE_GROUP_NO_SIMILAR, RATIO)
    spy.assert_called_once()
    assert result.equals(ONE_GROUP_NO_SIMILAR)


def test_more_groups_two_similar_titles(mocker: Mocker):
    spy = mocker.spy(ArticlesSimilarityFilter, "_get_single_group_index")
    result = SIMILARITY_FILTER.filter(MORE_GROUPS_TWO_SIMILAR, RATIO)
    spy.assert_not_called()
    assert result.shape[0] == 3
    assert result[Column.AUTHORS].tolist() == ["a", "b", "c"]
    recent_dates = ["2025-06-01", "2025-06-01", "2025-06-01"]
    assert result[Column.DATE].tolist() == recent_dates


def test_more_groups_more_similar_titles(mocker: Mocker):
    spy = mocker.spy(ArticlesSimilarityFilter, "_get_single_group_index")
    result = SIMILARITY_FILTER.filter(MORE_GROUPS_MORE_SIMILAR, RATIO)
    spy.assert_not_called()
    assert result.shape[0] == 3
    assert result[Column.AUTHORS].tolist() == ["a", "b", "c"]
    recent_dates = ["2025-06-04", "2025-05-03", "2025-04-02"]
    assert result[Column.DATE].tolist() == recent_dates


def test_more_groups_no_similar_titles(mocker: Mocker):
    spy = mocker.spy(ArticlesSimilarityFilter, "_get_single_group_index")
    result = SIMILARITY_FILTER.filter(MORE_GROUPS_NO_SIMILAR, RATIO)
    spy.assert_not_called()
    assert result.shape[0] == 9 and result.equals(MORE_GROUPS_NO_SIMILAR)


def test_to_datetime_no_left(mocker: Mocker):
    spy_to_datetime = mocker.patch(TO_DATETIME, wraps=to_datetime)
    spy_dropna = mocker.spy(DataFrame, "dropna")
    spy_log_debug = mocker.patch(**LOG_DEBUG)

    result = SIMILARITY_FILTER.filter(NO_DATETIME_LEFT, RATIO)
    df_to_datetime: Series = spy_to_datetime.call_args_list[0].args[0]
    df_dropna: DataFrame = spy_dropna.call_args_list[0].args[0]

    spy_log_debug.assert_called_once_with({"invalids_datetime": 0})
    spy_to_datetime.assert_called_once()
    spy_dropna.assert_called_once()

    assert all(isinstance(value, str) for value in df_to_datetime)
    assert all(isna(value) for value in df_dropna[Column.DATE])
    assert result.equals(NO_DATETIME_LEFT)


def test_to_datetime_one_left(mocker: Mocker):
    spy_to_datetime = mocker.patch(TO_DATETIME, wraps=to_datetime)
    spy_dropna = mocker.spy(DataFrame, "dropna")
    spy_log_debug = mocker.patch(**LOG_DEBUG)

    result = SIMILARITY_FILTER.filter(ONE_DATETIME_LEFT, RATIO)
    df_to_datetime: DataFrame = spy_to_datetime.call_args_list[0].args[0]
    df_dropna: DataFrame = spy_dropna.call_args_list[0].args[0]

    spy_log_debug.assert_called_once_with({"invalids_datetime": 1})
    spy_to_datetime.assert_called_once()
    spy_dropna.assert_called_once()

    assert all(isinstance(value, str) for value in df_to_datetime)
    assert isinstance(df_dropna[Column.DATE].iloc[0], datetime)
    assert isna(df_dropna[Column.DATE].iloc[1])
    assert result.equals(ONE_DATETIME_LEFT)


def test_no_repeated_authors(mocker: Mocker):
    spy_dropna = mocker.spy(DataFrame, "dropna")
    spy_filter = mocker.spy(DataFrameGroupBy, "filter")
    result = SIMILARITY_FILTER.filter(NO_REPEATED_AUTHORS, RATIO)
    spy_dropna.assert_called_once()
    spy_filter.assert_not_called()
    assert result.equals(NO_REPEATED_AUTHORS)


def test_filter_drop_singles(mocker: Mocker):
    spy_groupby = mocker.spy(DataFrame, "groupby")
    spy_filter = mocker.spy(DataFrameGroupBy, "filter")

    result = SIMILARITY_FILTER.filter(MORE_GROUPS_TWO_SIMILAR, RATIO)
    df_group: DataFrameGroupBy = spy_filter.call_args_list[0].args[0]
    df: DataFrame = spy_groupby.call_args_list[1].args[0]

    assert result.shape[0] == df_group.ngroups == 3
    assert df.shape[0] == 4 and "c" not in df[Column.AUTHORS].values


def test_discard_one_older_similar():
    result = SIMILARITY_FILTER.filter(ONE_GROUP_TWO_SIMILAR, RATIO)
    assert result.shape[0] == 1 and ONE_GROUP_TWO_SIMILAR.shape[0] == 2
    assert result[Column.DATE].iloc[0] == "2025-06-01"


def test_discard_all_older_similar():
    result = SIMILARITY_FILTER.filter(ONE_GROUP_MORE_SIMILAR, RATIO)
    assert result.shape[0] == 1 and ONE_GROUP_MORE_SIMILAR.shape[0] == 5
    assert result[Column.DATE].iloc[0] == "2025-05-05"


def test_cancelled_error(mocker: Mocker):
    mocker.patch(**CANCELLED)
    with raises(ServiceUnavailable) as info:
        SIMILARITY_FILTER.filter(MORE_GROUPS_TWO_SIMILAR, RATIO)
    assert_http_error(info, HTTP_503, ExcMsg.CANCELLED_ERROR)
    assert info.value.errors[0]["type"] == fqn(CancelledError)
    assert info.value.errors[0]["detail"] == "any"


def test_drop_similar(mocker: Mocker):
    spy_drop = mocker.spy(DataFrame, "drop")
    spy_reset = mocker.spy(DataFrame, "reset_index")

    result = SIMILARITY_FILTER.filter(ONE_GROUP_MORE_SIMILAR, RATIO)
    df_in: DataFrame = spy_drop.call_args_list[0].args[0]
    similar_titles: set = spy_drop.call_args_list[0].args[1]
    df_out: DataFrame = spy_reset.call_args_list[0].args[0]

    assert result.shape[0] == 1 and len(similar_titles) == 4
    assert df_in.shape[0] == 5 and df_out.shape[0] == 1
