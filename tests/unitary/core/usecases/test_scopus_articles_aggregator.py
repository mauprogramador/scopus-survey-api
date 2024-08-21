from collections import Counter

from pandas import DataFrame
from pytest_mock import MockerFixture

from app.core.config.scopus import COLUMNS_MAPPING
from tests.mocks import unitary as mock
from tests.mocks.common import SCRAPE_COLUMNS, SEARCH_PARAMS
from tests.mocks.fixtures import ARTICLES_AGGREGATOR, SEARCH_ARTICLES


def test_one_row(mocker: MockerFixture):
    mocker.patch(SEARCH_ARTICLES, return_value=mock.ONE_ARTICLE)
    spy = mocker.spy(DataFrame, "to_csv")

    response = ARTICLES_AGGREGATOR.get_articles(SEARCH_PARAMS)
    df_spy: DataFrame = spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert df_spy.shape == (1, 10)


def test_more_rows(mocker: MockerFixture):
    mocker.patch(SEARCH_ARTICLES, return_value=mock.MORE_ARTICLES)
    spy = mocker.spy(DataFrame, "to_csv")

    response = ARTICLES_AGGREGATOR.get_articles(SEARCH_PARAMS)
    df_spy: DataFrame = spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert df_spy.shape == (7, 10)


def test_drop_exact_duplicates(mocker: MockerFixture):
    mocker.patch(SEARCH_ARTICLES, return_value=mock.EXACT_DUPLICATES)
    spy_in = mocker.spy(DataFrame, "drop_duplicates")
    spy_out = mocker.spy(DataFrame, "reset_index")

    response = ARTICLES_AGGREGATOR.get_articles(SEARCH_PARAMS)
    df_in: DataFrame = spy_in.call_args_list[0].args[0]
    df_out: DataFrame = spy_out.call_args_list[0].args[0]

    assert response.status_code == 200
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1


def test_insert_two_columns(mocker: MockerFixture):
    mocker.patch(SEARCH_ARTICLES, return_value=mock.ONE_ARTICLE)
    spy_in = mocker.spy(DataFrame, "reset_index")
    spy_out = mocker.spy(DataFrame, "rename")

    response = ARTICLES_AGGREGATOR.get_articles(SEARCH_PARAMS)
    df_in: DataFrame = spy_in.call_args_list[0].args[0]
    df_out: DataFrame = spy_out.call_args_list[0].args[0]

    assert response.status_code == 200
    assert df_in.shape[1] + 2 == df_out.shape[1]


def test_one_row_scraping_data(mocker: MockerFixture):
    mocker.patch(SEARCH_ARTICLES, return_value=mock.ONE_ARTICLE)
    spy = mocker.spy(DataFrame, "rename")

    response = ARTICLES_AGGREGATOR.get_articles(SEARCH_PARAMS)
    df: DataFrame = spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert df[SCRAPE_COLUMNS].values.flatten().sum().count("any") == 3


def test_more_rows_scraping_data(mocker: MockerFixture):
    mocker.patch(SEARCH_ARTICLES, return_value=mock.MORE_ARTICLES)
    spy = mocker.spy(DataFrame, "rename")

    response = ARTICLES_AGGREGATOR.get_articles(SEARCH_PARAMS)
    df: DataFrame = spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert df[SCRAPE_COLUMNS].values.flatten().sum().count("any") == 21


def test_rename_columns(mocker: MockerFixture):
    mocker.patch(SEARCH_ARTICLES, return_value=mock.ONE_ARTICLE)
    spy_in = mocker.spy(DataFrame, "rename")
    spy_out = mocker.spy(DataFrame, "drop_duplicates")

    response = ARTICLES_AGGREGATOR.get_articles(SEARCH_PARAMS)
    df_in: DataFrame = spy_in.call_args_list[0].args[0]
    df_out: DataFrame = spy_out.call_args_list[1].args[0]

    columns_in = list(COLUMNS_MAPPING.keys())
    columns_out = list(COLUMNS_MAPPING.values())

    new_columns = ["Abstract", "Authors"]
    columns_in.extend(new_columns)
    columns_out.extend(new_columns)

    assert response.status_code == 200
    assert Counter(df_in.columns) != Counter(df_out.columns)
    assert Counter(df_in.columns) == Counter(columns_in)
    assert Counter(df_out.columns) == Counter(columns_out)


def test_drop_same_title_and_authors(mocker: MockerFixture):
    mocker.patch(SEARCH_ARTICLES, return_value=mock.SAME_TITLE_AND_AUTHORS)
    spy_in = mocker.spy(DataFrame, "drop_duplicates")
    spy_out = mocker.spy(DataFrame, "reset_index")

    response = ARTICLES_AGGREGATOR.get_articles(SEARCH_PARAMS)
    df_in: DataFrame = spy_in.call_args_list[1].args[0]
    df_out: DataFrame = spy_out.call_args_list[1].args[0]

    assert response.status_code == 200
    assert df_in.shape[0] > df_out.shape[0]
    assert df_out.shape[0] == 1
