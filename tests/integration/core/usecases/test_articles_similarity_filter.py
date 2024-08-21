import pytest
from pandas import DataFrame, Series
from pytest_mock import MockerFixture

from tests.helpers.utils import app_request, content_response
from tests.mocks import common as data
from tests.mocks import integration as mock
from tests.mocks.fixtures import REQUEST


@pytest.mark.asyncio
async def test_two_similar_titles(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.TWO_SIMILAR_TITLES)
    spy = mocker.spy(Series, "value_counts")
    response = await app_request(data.URL)
    content = content_response(response)
    authors_counts: Series = spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert authors_counts.value_counts().shape[0] == 1
    assert content.shape[0] == 1


@pytest.mark.asyncio
async def test_more_similar_titles(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.MORE_SIMILAR_TITLES)
    spy = mocker.spy(Series, "value_counts")
    response = await app_request(data.URL)
    content = content_response(response)
    authors_counts: Series = spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert authors_counts.value_counts().shape[0] == 3
    assert content.shape[0] == 3


@pytest.mark.asyncio
async def test_no_repeated_authors(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.NO_REPEATED_AUTHORS)
    spy = mocker.spy(Series, "value_counts")
    response = await app_request(data.URL)
    content = content_response(response)
    authors_counts: Series = spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert authors_counts.value_counts().shape[0] == 2
    assert content.shape[0] == 2


@pytest.mark.asyncio
async def test_no_similar_titles(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.NO_SIMILAR_TITLES)
    spy = mocker.spy(Series, "value_counts")
    response = await app_request(data.URL)
    content = content_response(response)
    authors_counts: Series = spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert authors_counts.value_counts().shape[0] == 1
    assert content.shape[0] == 2


@pytest.mark.asyncio
async def test_drop_similar(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.TWO_SIMILAR_TITLES)
    spy_in = mocker.spy(DataFrame, "drop")
    spy_out = mocker.spy(DataFrame, "reset_index")
    response = await app_request(data.URL)
    content = content_response(response)
    df_in: DataFrame = spy_in.call_args_list[0].args[0]
    similar_titles: set = spy_in.call_args_list[0].args[1]
    df_out: DataFrame = spy_out.call_args_list[2].args[0]

    assert response.status_code == 200
    assert content.shape[0] == 1
    assert len(similar_titles) == 1
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1
