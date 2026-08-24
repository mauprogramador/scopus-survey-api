from datetime import datetime

import pandas as pd
from pandas import DataFrame, Series
from pandas.api.typing import DataFrameGroupBy
from pytest_mock import MockerFixture as Mocker

from src.core.use_cases.similarity_filter import SimilarityFilter
from src.infra.utils import logger
from tests.mocks.helpers import fqn, spec
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


TO_DATETIME = fqn(SimilarityFilter, pd.to_datetime, "pd")
LOG_DEBUG = spec(SimilarityFilter, logger.debug, "logger")
RATIO = 80


def test_one_group_two_similar_titles(mocker: Mocker):
    spy = mocker.spy(SimilarityFilter, "_get_group_similar_title_indices")
    df = SimilarityFilter().filter(ONE_GROUP_TWO_SIMILAR, RATIO)
    spy.assert_called_once()
    assert df.shape[0] == 1
    assert df["authors"].iloc[0] == "a"
    assert df["date"].iloc[0] == "2025-06-01"


def test_one_group_more_similar_titles(mocker: Mocker):
    spy = mocker.spy(SimilarityFilter, "_get_group_similar_title_indices")
    df = SimilarityFilter().filter(ONE_GROUP_MORE_SIMILAR, RATIO)
    spy.assert_called_once()
    assert df.shape[0] == 1
    assert df["authors"].iloc[0] == "a"
    assert df["date"].iloc[0] == "2025-05-05"


def test_one_group_no_similar_titles(mocker: Mocker):
    spy = mocker.spy(SimilarityFilter, "_get_group_similar_title_indices")
    df = SimilarityFilter().filter(ONE_GROUP_NO_SIMILAR, RATIO)
    spy.assert_called_once()
    assert df.equals(ONE_GROUP_NO_SIMILAR)


def test_more_groups_two_similar_titles(mocker: Mocker):
    spy = mocker.spy(SimilarityFilter, "_get_group_similar_title_indices")
    df = SimilarityFilter().filter(MORE_GROUPS_TWO_SIMILAR, RATIO)
    assert df.shape[0] == 3 and spy.call_count == 2
    assert df["authors"].tolist() == ["a", "b", "c"]
    recent_dates = ["2025-06-01", "2025-06-01", "2025-06-01"]
    assert df["date"].tolist() == recent_dates


def test_more_groups_more_similar_titles(mocker: Mocker):
    spy = mocker.spy(SimilarityFilter, "_get_group_similar_title_indices")
    df = SimilarityFilter().filter(MORE_GROUPS_MORE_SIMILAR, RATIO)
    assert df.shape[0] == 3 and spy.call_count == 3
    assert df["authors"].tolist() == ["a", "b", "c"]
    recent_dates = ["2025-06-04", "2025-05-03", "2025-04-02"]
    assert df["date"].tolist() == recent_dates


def test_more_groups_no_similar_titles(mocker: Mocker):
    spy = mocker.spy(SimilarityFilter, "_get_group_similar_title_indices")
    df = SimilarityFilter().filter(MORE_GROUPS_NO_SIMILAR, RATIO)
    assert spy.call_count == 3
    assert df.shape[0] == 9 and df.equals(MORE_GROUPS_NO_SIMILAR)


def test_to_datetime_no_left(mocker: Mocker):
    spy_to_datetime = mocker.patch(TO_DATETIME, wraps=pd.to_datetime)
    spy_dropna = mocker.spy(DataFrame, "dropna")
    spy_log_debug = mocker.patch(**LOG_DEBUG)

    df = SimilarityFilter().filter(NO_DATETIME_LEFT, RATIO)
    df_to_datetime: Series = spy_to_datetime.call_args_list[0].args[0]
    df_dropna: DataFrame = spy_dropna.call_args_list[0].args[0]

    assert spy_log_debug.call_args_list[0].kwargs["invalid_datetimes"] == 0
    spy_to_datetime.assert_called_once()
    spy_dropna.assert_called_once()

    assert all(isinstance(value, str) for value in df_to_datetime)
    assert all(pd.isna(value) for value in df_dropna["date"])
    assert df.equals(NO_DATETIME_LEFT)


def test_to_datetime_one_left(mocker: Mocker):
    spy_to_datetime = mocker.patch(TO_DATETIME, wraps=pd.to_datetime)
    spy_dropna = mocker.spy(DataFrame, "dropna")
    spy_log_debug = mocker.patch(**LOG_DEBUG)

    df = SimilarityFilter().filter(ONE_DATETIME_LEFT, RATIO)
    df_to_datetime: DataFrame = spy_to_datetime.call_args_list[0].args[0]
    df_dropna: DataFrame = spy_dropna.call_args_list[0].args[0]

    assert spy_log_debug.call_args_list[0].kwargs["invalid_datetimes"] == 1
    spy_to_datetime.assert_called_once()
    spy_dropna.assert_called_once()

    assert all(isinstance(value, str) for value in df_to_datetime)
    assert isinstance(df_dropna["date"].iloc[0], datetime)
    assert pd.isna(df_dropna["date"].iloc[1])
    assert df.equals(ONE_DATETIME_LEFT)


def test_no_repeated_authors(mocker: Mocker):
    spy_dropna = mocker.spy(DataFrame, "dropna")
    spy_filter = mocker.spy(DataFrameGroupBy, "filter")
    df = SimilarityFilter().filter(NO_REPEATED_AUTHORS, RATIO)
    spy_dropna.assert_called_once()
    spy_filter.assert_not_called()
    assert df.equals(NO_REPEATED_AUTHORS)


def test_filter_drop_singles(mocker: Mocker):
    spy_groupby = mocker.spy(DataFrame, "groupby")
    spy_filter = mocker.spy(DataFrameGroupBy, "filter")

    df = SimilarityFilter().filter(MORE_GROUPS_TWO_SIMILAR, RATIO)
    df_filter: DataFrameGroupBy = spy_filter.call_args_list[0].args[0]
    df_group: DataFrame = spy_groupby.call_args_list[1].args[0]

    assert df.shape[0] == df_filter.ngroups == 3
    assert df_group.shape[0] == 4
    assert "c" not in df_group["authors"].values


def test_discard_one_older_similar():
    df = SimilarityFilter().filter(ONE_GROUP_TWO_SIMILAR, RATIO)
    assert df.shape[0] == 1 and ONE_GROUP_TWO_SIMILAR.shape[0] == 2
    assert df["date"].iloc[0] == "2025-06-01"


def test_discard_all_older_similar():
    df = SimilarityFilter().filter(ONE_GROUP_MORE_SIMILAR, RATIO)
    assert df.shape[0] == 1 and ONE_GROUP_MORE_SIMILAR.shape[0] == 5
    assert df["date"].iloc[0] == "2025-05-05"


def test_drop_similar(mocker: Mocker):
    spy_drop = mocker.spy(DataFrame, "drop")
    spy_reset = mocker.spy(DataFrame, "reset_index")

    df = SimilarityFilter().filter(ONE_GROUP_MORE_SIMILAR, RATIO)
    df_drop: DataFrame = spy_drop.call_args_list[0].args[0]
    similar_titles: set = spy_drop.call_args_list[0].kwargs["index"]
    df_reset: DataFrame = spy_reset.call_args_list[0].args[0]

    assert df.shape[0] == 1 and len(similar_titles) == 4
    assert df_drop.shape[0] == 5 and df_reset.shape[0] == 1
