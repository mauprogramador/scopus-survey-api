from pandas import DataFrame
from pytest_mock import MockerFixture

from tests.mocks import unitary as mock
from tests.mocks.common import SEARCH_PARAMS
from tests.mocks.fixtures import (
    ARTICLES_AGGREGATOR,
    RETRIEVE_ABSTRACT,
    SEARCH_ARTICLES,
)


def test_one_row(mocker: MockerFixture):
    mocker.patch(SEARCH_ARTICLES, return_value=mock.ONE_ENTRY)
    mocker.patch(RETRIEVE_ABSTRACT, return_value=mock.ARTICLES.iloc[0:1])
    spy = mocker.spy(DataFrame, "to_csv")

    response = ARTICLES_AGGREGATOR.get_articles(SEARCH_PARAMS)
    df_spy: DataFrame = spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert df_spy.shape == (1, 11)


def test_more_rows(mocker: MockerFixture):
    mocker.patch(SEARCH_ARTICLES, return_value=mock.MORE_ENTRIES)
    mocker.patch(RETRIEVE_ABSTRACT, return_value=mock.ARTICLES)
    spy = mocker.spy(DataFrame, "to_csv")

    response = ARTICLES_AGGREGATOR.get_articles(SEARCH_PARAMS)
    df_spy: DataFrame = spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert df_spy.shape == (1, 11)


def test_drop_exact_duplicates(mocker: MockerFixture):
    mocker.patch(SEARCH_ARTICLES, return_value=mock.ONE_ENTRY)
    mocker.patch(RETRIEVE_ABSTRACT, return_value=mock.EXACT_DUPLICATES)
    spy_in = mocker.spy(DataFrame, "drop_duplicates")
    spy_out = mocker.spy(DataFrame, "reset_index")

    response = ARTICLES_AGGREGATOR.get_articles(SEARCH_PARAMS)
    df_in: DataFrame = spy_in.call_args_list[0].args[0]
    df_out: DataFrame = spy_out.call_args_list[0].args[0]

    assert response.status_code == 200
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1


def test_drop_same_title_and_authors(mocker: MockerFixture):
    mocker.patch(SEARCH_ARTICLES, return_value=mock.ONE_ENTRY)
    mocker.patch(RETRIEVE_ABSTRACT, return_value=mock.SAME_TITLE_AND_AUTHORS)
    spy_in = mocker.spy(DataFrame, "drop_duplicates")
    spy_out = mocker.spy(DataFrame, "reset_index")

    response = ARTICLES_AGGREGATOR.get_articles(SEARCH_PARAMS)
    df_in: DataFrame = spy_in.call_args_list[1].args[0]
    df_out: DataFrame = spy_out.call_args_list[1].args[0]

    assert response.status_code == 200
    assert df_in.shape[0] > df_out.shape[0]
    assert df_out.shape[0] == 1
