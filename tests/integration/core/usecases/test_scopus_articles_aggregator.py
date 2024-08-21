from collections import Counter

import pytest
from pandas import DataFrame
from pytest_mock import MockerFixture

from app.core.config.scopus import COLUMNS_MAPPING, NULL
from tests.helpers.utils import app_request, content_response
from tests.mocks import integration as mock
from tests.mocks.common import SCRAPE_COLUMNS, URL
from tests.mocks.fixtures import REQUEST


@pytest.mark.asyncio
async def test_one_row(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ONE_PAGE)
    response = await app_request(URL)

    assert response.status_code == 200
    assert content_response(response).shape == (1, 10)


@pytest.mark.asyncio
async def test_more_rows(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.MORE_PAGES)
    response = await app_request(URL)

    assert response.status_code == 200
    assert content_response(response).shape == (7, 10)


@pytest.mark.asyncio
async def test_drop_exact_duplicates(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.EXACT_DUPLICATES)
    spy_in = mocker.spy(DataFrame, "drop_duplicates")
    spy_out = mocker.spy(DataFrame, "reset_index")

    response = await app_request(URL)
    df_in: DataFrame = spy_in.call_args_list[0].args[0]
    df_out: DataFrame = spy_out.call_args_list[0].args[0]

    assert response.status_code == 200
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1
    assert content_response(response).shape == (1, 10)


@pytest.mark.asyncio
async def test_insert_two_columns(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ONE_PAGE)
    spy_in = mocker.spy(DataFrame, "reset_index")
    spy_out = mocker.spy(DataFrame, "rename")

    response = await app_request(URL)
    content = content_response(response)
    df_in: DataFrame = spy_in.call_args_list[0].args[0]
    df_out: DataFrame = spy_out.call_args_list[0].args[0]

    assert response.status_code == 200
    assert df_in.shape == (1, 8) and df_out.shape == (1, 10)
    assert df_in.shape[1] + 2 == df_out.shape[1] and content.shape == (1, 10)
    assert content.columns.isin(mock.INSERTED_COLUMNS).any()


@pytest.mark.asyncio
async def test_one_row_scraping_data(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ONE_PAGE)
    spy = mocker.spy(DataFrame, "rename")

    response = await app_request(URL)
    df: DataFrame = spy.call_args_list[0].args[0]
    data: str = df[SCRAPE_COLUMNS].values.flatten().sum()

    assert response.status_code == 200
    assert data.count(NULL) == 2 and data.count("any") == 1


@pytest.mark.asyncio
async def test_more_rows_scraping_data(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.MORE_PAGES)
    spy = mocker.spy(DataFrame, "rename")

    response = await app_request(URL)
    df: DataFrame = spy.call_args_list[0].args[0]
    data: str = df[SCRAPE_COLUMNS].values.flatten().sum()

    assert response.status_code == 200
    assert data.count(NULL) == 14 and data.count("any") == 7


@pytest.mark.asyncio
async def test_rename_columns(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ONE_PAGE)
    spy_in = mocker.spy(DataFrame, "rename")
    spy_out = mocker.spy(DataFrame, "drop_duplicates")

    response = await app_request(URL)
    df_in: DataFrame = spy_in.call_args_list[0].args[0]
    df_out: DataFrame = spy_out.call_args_list[1].args[0]

    columns_in = list(COLUMNS_MAPPING.keys())
    columns_out = list(COLUMNS_MAPPING.values())

    columns_in.extend(mock.INSERTED_COLUMNS)
    columns_out.extend(mock.INSERTED_COLUMNS)

    assert response.status_code == 200
    assert Counter(df_in.columns) != Counter(df_out.columns)
    assert Counter(df_in.columns) == Counter(columns_in)
    assert Counter(df_out.columns) == Counter(columns_out)


@pytest.mark.asyncio
async def test_drop_same_title_and_authors(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.SAME_TITLE_AND_AUTHORS)
    spy_in = mocker.spy(DataFrame, "drop_duplicates")
    spy_out = mocker.spy(DataFrame, "reset_index")

    response = await app_request(URL)
    df_in: DataFrame = spy_in.call_args_list[1].args[0]
    df_out: DataFrame = spy_out.call_args_list[1].args[0]

    assert response.status_code == 200
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1
    assert content_response(response).shape == (1, 10)
