import pytest
from pandas import DataFrame
from pytest_mock import MockerFixture

from tests.helpers.utils import app_request, content_response
from tests.mocks import integration as mock
from tests.mocks.common import URL
from tests.mocks.fixtures import REQUEST


@pytest.mark.asyncio
async def test_one_row(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ONE_PAGE)
    response = await app_request(URL)
    assert response.status_code == 200
    assert content_response(response).shape == (1, 11)


@pytest.mark.asyncio
async def test_more_rows(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.MORE_PAGES)
    response = await app_request(URL)
    assert response.status_code == 200
    assert content_response(response).shape == (7, 11)


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
    assert content_response(response).shape == (1, 11)


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
    assert content_response(response).shape == (1, 11)
