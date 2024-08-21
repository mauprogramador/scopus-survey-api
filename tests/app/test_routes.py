from tempfile import TemporaryDirectory

import pytest
from fastapi.templating import Jinja2Templates
from pytest_mock import MockerFixture

from app.core.config.config import TOKEN
from tests.data import mocks
from tests.data.request import app_request
from tests.data.utils import get_csv_file


@pytest.mark.asyncio
async def test_search_articles(mocker: MockerFixture):
    with TemporaryDirectory() as tmpdir:
        mocker.patch(mocks.SEARCH_ARTICLES, return_value=get_csv_file(tmpdir))
        response = await app_request(mocks.URL)
        assert response.status_code == 200
        assert len(response.text)
        assert mocks.CSV_CONTENT_TYPE in response.headers.items()


@pytest.mark.asyncio
async def test_render_web_application(mocker: MockerFixture):
    template_spy = mocker.spy(Jinja2Templates, 'TemplateResponse')
    response = await app_request(mocks.BASE_URL)
    context: dict = template_spy.call_args_list[0].args[3]
    assert response.status_code == 200
    assert len(response.text)
    assert mocks.HTML_CONTENT_TYPE in response.headers.items()
    assert context['token'] == TOKEN


@pytest.mark.asyncio
async def test_render_web_table_content_none(mocker: MockerFixture):
    mocker.patch(mocks.CSV_TABLE, return_value=None)
    template_spy = mocker.spy(Jinja2Templates, 'TemplateResponse')
    response = await app_request(mocks.TABLE_URL)
    context: dict = template_spy.call_args_list[0].args[3]
    assert response.status_code == 200
    assert len(response.text)
    assert mocks.HTML_CONTENT_TYPE in response.headers.items()
    assert not context['content']


@pytest.mark.asyncio
async def test_render_web_table_with_content(mocker: MockerFixture):
    mocker.patch(mocks.CSV_TABLE, return_value=mocks.FAKE_CSV_DATA)
    template_spy = mocker.spy(Jinja2Templates, 'TemplateResponse')
    response = await app_request(mocks.TABLE_URL)
    context: dict = template_spy.call_args_list[0].args[3]
    assert response.status_code == 200
    assert len(response.text)
    assert mocks.HTML_CONTENT_TYPE in response.headers.items()
    assert context['content'] == mocks.FAKE_CSV_DATA
