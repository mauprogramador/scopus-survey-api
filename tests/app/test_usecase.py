from collections import Counter

import pytest
from pandas import DataFrame, Series
from pytest_mock import MockerFixture

from app.core.usecase import Scopus
from app.gateway.api_config import ApiConfig
from tests.data import mocks
from tests.data.request import app_request


@pytest.mark.asyncio
async def test_unit_usecase_200(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_ARTICLES,
    )
    mocker.patch(
        mocks.SCOPUS_API_SCRAPING_ARTICLE,
        return_value=mocks.FAKE_SCOPUS_API_SCRAPING_ARTICLE,
    )
    response = Scopus().search_articles(mocks.FAKE_API_PARAMS)
    assert response.status_code == 200
    assert response.media_type == 'text/csv'
    assert mocks.CSV_CONTENT_TYPE in response.headers.items()


@pytest.mark.asyncio
async def test_usecase_remove_column(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_ARTICLES,
    )
    mocker.patch(
        mocks.SCOPUS_API_SCRAPING_ARTICLE,
        return_value=mocks.FAKE_SCOPUS_API_SCRAPING_ARTICLE,
    )

    input_spy = mocker.spy(DataFrame, 'drop_duplicates')
    response = await app_request(mocks.URL)
    input_dataframe: DataFrame = input_spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert Scopus.LINK_COLUMN in mocks.FAKE_ARTICLES[0]
    assert Scopus.LINK_COLUMN not in input_dataframe.columns


@pytest.mark.asyncio
async def test_usecase_remove_all_duplicates(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_DUPLICATES_ARTICLES,
    )
    mocker.patch(
        mocks.SCOPUS_API_SCRAPING_ARTICLE,
        return_value=mocks.FAKE_SCOPUS_API_SCRAPING_ARTICLE,
    )

    input_spy = mocker.spy(DataFrame, 'drop_duplicates')
    output_spy = mocker.spy(DataFrame, 'insert')

    response = await app_request(mocks.URL)

    input_dataframe: DataFrame = input_spy.call_args_list[0].args[0]
    output_dataframe: DataFrame = output_spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert input_dataframe.shape[0] > output_dataframe.shape[0]


@pytest.mark.asyncio
async def test_usecase_insert_two_columns(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_ARTICLES,
    )
    mocker.patch(
        mocks.SCOPUS_API_SCRAPING_ARTICLE,
        return_value=mocks.FAKE_SCOPUS_API_SCRAPING_ARTICLE,
    )

    input_spy = mocker.spy(DataFrame, 'drop_duplicates')
    output_spy = mocker.spy(DataFrame, 'apply')

    response = await app_request(mocks.URL)

    input_dataframe: DataFrame = input_spy.call_args_list[0].args[0]
    output_dataframe: DataFrame = output_spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert output_dataframe.shape[1] == input_dataframe.shape[1] + 2


@pytest.mark.asyncio
async def test_usecase_scraping_data(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_DUPLICATES_ARTICLES,
    )
    mocker.patch(mocks.HTTP_HELPER_REQUEST, return_value=mocks.FAKE_TEMPLATE)

    input_spy = mocker.spy(DataFrame, 'apply')
    output_spy = mocker.spy(DataFrame, 'rename')

    response = await app_request(mocks.URL)

    input_series: Series = input_spy.call_args_list[0].args[0].loc[0]
    output_series: Series = output_spy.call_args_list[0].args[0].loc[0]

    scopus_id = output_series[Scopus.SCOPUS_ID_KEY].split(':')[1]
    output_url = ApiConfig.get_article_page_url(scopus_id)

    assert response.status_code == 200
    assert input_series[Scopus.URL_COLUMN] != output_series[Scopus.URL_COLUMN]
    assert output_series[Scopus.URL_COLUMN] == output_url

    output_authors = output_series[Scopus.AUTHORS_COLUMN]
    assert input_series[Scopus.AUTHORS_COLUMN] != output_authors
    assert len(output_authors) > 2

    output_abstract = output_series[Scopus.ABSTRACT_COLUMN]
    assert input_series[Scopus.ABSTRACT_COLUMN] != output_abstract
    assert len(output_abstract) > 10


@pytest.mark.asyncio
async def test_usecase_get_scraping_data_method(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_DUPLICATES_ARTICLES,
    )
    mocker.patch(
        mocks.SCOPUS_API_SCRAPING_ARTICLE,
        return_value=mocks.FAKE_SCOPUS_API_SCRAPING_ARTICLE,
    )

    input_spy = mocker.spy(DataFrame, 'rename')
    response = await app_request(mocks.URL)
    input_spy_row: DataFrame = input_spy.call_args_list[0].args[0].iloc[0]

    assert response.status_code == 200
    assert input_spy_row[Scopus.URL_COLUMN] == mocks.FAKE_LINK
    assert input_spy_row[Scopus.AUTHORS_COLUMN] == mocks.FAKE_AUTHORS
    assert input_spy_row[Scopus.ABSTRACT_COLUMN] == mocks.FAKE_ABSTRACT


@pytest.mark.asyncio
async def test_usecase_rename_columns(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_DUPLICATES_ARTICLES,
    )
    mocker.patch(mocks.HTTP_HELPER_REQUEST, return_value=mocks.FAKE_TEMPLATE)

    input_spy = mocker.spy(DataFrame, 'rename')
    output_spy = mocker.spy(DataFrame, 'drop_duplicates')

    response = await app_request(mocks.URL)

    input_columns: DataFrame = input_spy.call_args_list[0].args[0].columns
    output_columns: DataFrame = output_spy.call_args_list[1].args[0].columns

    final_input_columns = list(ApiConfig.MAPPINGS.values())
    final_output_columns = list(ApiConfig.MAPPINGS.keys())

    new_columns = ['Abstract', 'Authors']
    final_input_columns.extend(new_columns)
    final_output_columns.extend(new_columns)

    assert response.status_code == 200
    assert Counter(input_columns) != Counter(output_columns)
    assert Counter(input_columns) == Counter(final_output_columns)
    assert Counter(output_columns) == Counter(final_input_columns)


@pytest.mark.asyncio
async def test_usecase_remove_duplicates(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_DUPLICATES_ARTICLES,
    )
    mocker.patch(mocks.HTTP_HELPER_REQUEST, return_value=mocks.FAKE_TEMPLATE)

    input_spy = mocker.spy(DataFrame, 'drop_duplicates')
    output_spy = mocker.spy(DataFrame, 'to_csv')

    response = await app_request(mocks.URL)

    input_dataframe: DataFrame = input_spy.call_args_list[1].args[0]
    output_dataframe: DataFrame = output_spy.call_args_list[0].args[0]

    assert response.status_code == 200
    assert input_dataframe.shape[0] > output_dataframe.shape[0]
    assert output_dataframe.shape[0] == 1


@pytest.mark.asyncio
async def test_usecase_no_groups(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_DUPLICATE_AUTHORS_ARTICLES,
    )
    mocker.patch(mocks.HTTP_HELPER_REQUEST, return_value=mocks.FAKE_TEMPLATE)
    mocker.patch(mocks.RENAME_DATAFRAME, return_value=mocks.FAKE_DATA_NO_GROUP)

    group_spy = mocker.spy(DataFrame, 'groupby')
    csv_spy = mocker.spy(DataFrame, 'to_csv')

    response = await app_request(mocks.URL)

    group_dataframe: DataFrame = group_spy.call_args_list[0].args[0]
    csv_dataframe: DataFrame = csv_spy.call_args_list[0].args[0]
    ngroups = mocks.FAKE_DATA_NO_GROUP.groupby(Scopus.AUTHORS_COLUMN).ngroups

    assert response.status_code == 200
    assert group_dataframe.shape[0] == mocks.FAKE_DATA_NO_GROUP.shape[0]
    assert group_dataframe.shape[0] == ngroups
    assert csv_dataframe.equals(mocks.FAKE_DATA_NO_GROUP)


@pytest.mark.asyncio
async def test_usecase_one_group(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_DUPLICATE_AUTHORS_ARTICLES,
    )
    mocker.patch(mocks.HTTP_HELPER_REQUEST, return_value=mocks.FAKE_TEMPLATE)
    mocker.patch(
        mocks.RENAME_DATAFRAME, return_value=mocks.FAKE_DATA_ONE_GROUP
    )

    group_spy = mocker.spy(DataFrame, 'groupby')
    list_spy = mocker.spy(Series, 'tolist')
    drop_spy = mocker.spy(DataFrame, 'drop')
    csv_spy = mocker.spy(DataFrame, 'to_csv')

    response = await app_request(mocks.URL)

    group_dataframe: DataFrame = group_spy.call_args_list[0].args[0]
    list_series: Series = list_spy.call_args_list[0].args[0]
    similar_titles: list = drop_spy.call_args_list[0].args[1]
    csv_dataframe: DataFrame = csv_spy.call_args_list[0].args[0]

    ngroups = mocks.FAKE_DATA_ONE_GROUP.groupby(Scopus.AUTHORS_COLUMN).ngroups
    authors = csv_dataframe[Scopus.AUTHORS_COLUMN].to_list()

    assert response.status_code == 200
    assert group_dataframe.shape[0] == mocks.FAKE_DATA_ONE_GROUP.shape[0]
    assert group_dataframe.shape[0] != ngroups
    assert ngroups == 2 and list_series.shape[0] == 2
    assert similar_titles and len(similar_titles) == 1
    assert csv_dataframe.shape[0] == 2
    assert not csv_dataframe.equals(mocks.FAKE_DATA_ONE_GROUP)
    assert authors == ['any_author1', 'any_author2']


@pytest.mark.asyncio
async def test_usecase_groups(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_DUPLICATE_AUTHORS_ARTICLES,
    )
    mocker.patch(mocks.HTTP_HELPER_REQUEST, return_value=mocks.FAKE_TEMPLATE)
    mocker.patch(mocks.RENAME_DATAFRAME, return_value=mocks.FAKE_DATA_GROUPS)

    group_spy = mocker.spy(DataFrame, 'groupby')
    list_spy = mocker.spy(Series, 'tolist')
    drop_spy = mocker.spy(DataFrame, 'drop')
    csv_spy = mocker.spy(DataFrame, 'to_csv')

    response = await app_request(mocks.URL)

    group_dataframe: DataFrame = group_spy.call_args_list[0].args[0]
    list_series: Series = list_spy.call_args_list[0].args[0]
    similar_titles: list = drop_spy.call_args_list[0].args[1]
    csv_dataframe: DataFrame = csv_spy.call_args_list[0].args[0]

    ngroups = mocks.FAKE_DATA_GROUPS.groupby(Scopus.AUTHORS_COLUMN).ngroups
    authors = csv_dataframe[Scopus.AUTHORS_COLUMN].to_list()

    assert response.status_code == 200
    assert group_dataframe.shape[0] == mocks.FAKE_DATA_GROUPS.shape[0]
    assert group_dataframe.shape[0] != ngroups
    assert ngroups == 3 and list_series.shape[0] == 2
    assert similar_titles and len(similar_titles) == 3
    assert csv_dataframe.shape[0] == 3
    assert not csv_dataframe.equals(mocks.FAKE_DATA_GROUPS)
    assert authors == ['any_author1', 'any_author2', 'any_author3']
