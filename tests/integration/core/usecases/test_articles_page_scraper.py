import pytest
from pandas import DataFrame
from pytest_mock import MockerFixture

from app.adapters.gateway.scopus_article_page import ScopusArticlesPage
from app.core.common.messages import INTERRUPT_ERROR
from app.core.config.scopus import ABSTRACT_COLUMN, AUTHORS_COLUMN, NULL
from app.core.usecases.articles_page_scraper import ArticlesPageScraper
from app.framework.exceptions.http_exceptions import BaseExceptionResponse
from tests.helpers.utils import app_request, content_response
from tests.mocks import integration as mock
from tests.mocks.common import URL
from tests.mocks.fixtures import IS_SET, REQUEST
from tests.mocks.unitary import SCRAP_DATA


@pytest.mark.asyncio
async def test_scrape(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ONE_ROW)
    response = await app_request(URL)
    content = content_response(response)

    assert response.status_code == 200
    assert content.loc[0, AUTHORS_COLUMN] == SCRAP_DATA[1]
    assert content.loc[0, ABSTRACT_COLUMN] == SCRAP_DATA[2]


@pytest.mark.asyncio
async def test_template_null(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ONE_PAGE)
    response = await app_request(URL)
    content = content_response(response)

    assert response.status_code == 200
    assert content.loc[0, AUTHORS_COLUMN] == NULL
    assert content.loc[0, ABSTRACT_COLUMN] == NULL


@pytest.mark.asyncio
async def test_scrape_multiple(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.MORE_ROWS)
    response = await app_request(URL)
    content = content_response(response)
    authors_values = [SCRAP_DATA[1]] * 7
    abstract_values = [SCRAP_DATA[2]] * 7

    assert content.loc[:, AUTHORS_COLUMN].values.tolist() == authors_values
    assert content.loc[:, ABSTRACT_COLUMN].values.tolist() == abstract_values


@pytest.mark.asyncio
async def test_check_subset_copy_size(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ONE_PAGE)
    spy_in = mocker.spy(ArticlesPageScraper, "set_subset")
    spy_out = mocker.spy(ScopusArticlesPage, "get_articles_page")
    response = await app_request(URL)
    df_in: DataFrame = spy_in.call_args_list[0].args[1]
    df_out: DataFrame = spy_out.call_args_list[0].args[1]

    assert response.status_code == 200
    assert df_in.shape[1] == 3 and df_out.shape[1] == 3


@pytest.mark.asyncio
async def test_interrupt_error(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ONE_PAGE)
    mocker.patch(IS_SET, return_value=True)
    response = await app_request(URL)
    exc_response = BaseExceptionResponse.model_validate(response.json())

    assert response.status_code == 500
    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == INTERRUPT_ERROR
    assert exc_response.errors is None
