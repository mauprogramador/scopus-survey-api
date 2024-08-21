from pandas import DataFrame
from pytest_mock import MockerFixture

from app.core.config.scopus import AUTHORS_COLUMN
from tests.mocks import unitary as mock
from tests.mocks.fixtures import SIMILARITY_FILTER


def test_two_similar_titles():
    result = SIMILARITY_FILTER.filter(mock.TWO_SIMILAR_TITLES)
    authors_counts = mock.TWO_SIMILAR_TITLES[AUTHORS_COLUMN].value_counts()
    assert authors_counts.shape[0] == 1
    assert result.shape[0] == 1


def test_more_similar_titles():
    result = SIMILARITY_FILTER.filter(mock.MORE_SIMILAR_TITLES)
    authors_counts = mock.MORE_SIMILAR_TITLES[AUTHORS_COLUMN].value_counts()
    assert authors_counts.shape[0] == 3
    assert result.shape[0] == 3


def test_no_repeated_authors():
    result = SIMILARITY_FILTER.filter(mock.NO_REPEATED_AUTHORS)
    authors_counts = mock.NO_REPEATED_AUTHORS[AUTHORS_COLUMN].value_counts()
    assert authors_counts.shape[0] == mock.NO_REPEATED_AUTHORS.shape[0]
    assert result.equals(mock.NO_REPEATED_AUTHORS)


def test_no_similar_titles():
    result = SIMILARITY_FILTER.filter(mock.NO_SIMILAR_TITLES)
    authors_counts = mock.NO_SIMILAR_TITLES[AUTHORS_COLUMN].value_counts()
    assert authors_counts.shape[0] == 1
    assert result.equals(mock.NO_SIMILAR_TITLES)


def test_drop_similar(mocker: MockerFixture):
    spy_in = mocker.spy(DataFrame, "drop")
    spy_out = mocker.spy(DataFrame, "reset_index")

    result = SIMILARITY_FILTER.filter(mock.TWO_SIMILAR_TITLES)
    df_in: DataFrame = spy_in.call_args_list[0].args[0]
    similar_titles: set = spy_in.call_args_list[0].args[1]
    df_out: DataFrame = spy_out.call_args_list[0].args[0]

    assert result.shape[0] == 1
    assert len(similar_titles) == 1
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1
