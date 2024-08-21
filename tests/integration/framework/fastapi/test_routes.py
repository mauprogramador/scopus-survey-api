import pytest
from fastapi.templating import Jinja2Templates
from pytest_mock import MockerFixture

from app.core.config.config import TOKEN
from tests.helpers.utils import app_request
from tests.mocks import common as data
from tests.mocks.fixtures import READ_CSV, REQUEST
from tests.mocks.integration import ONE_PAGE


@pytest.mark.asyncio
async def test_search_articles(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=ONE_PAGE)
    response = await app_request(data.URL)

    assert response.status_code == 200 and response.text
    assert data.CSV_CONTENT_TYPE in response.headers.items()


@pytest.mark.asyncio
async def test_render_web_application(mocker: MockerFixture):
    template_spy = mocker.spy(Jinja2Templates, "TemplateResponse")
    response = await app_request(data.BASE_URL)
    context: dict = template_spy.call_args_list[0].args[3]

    assert response.status_code == 200 and response.text
    assert data.HTML_CONTENT_TYPE in response.headers.items()
    assert context.get("token") == TOKEN


@pytest.mark.asyncio
async def test_render_web_table_with_content(mocker: MockerFixture):
    mocker.patch(READ_CSV, return_value=data.CSV_DATA)
    template_spy = mocker.spy(Jinja2Templates, "TemplateResponse")
    response = await app_request(data.TABLE_URL)
    context: dict = template_spy.call_args_list[0].args[3]

    assert response.status_code == 200 and response.text
    assert data.HTML_CONTENT_TYPE in response.headers.items()
    assert context["content"] == data.CSV_DATA.to_numpy().tolist()


@pytest.mark.asyncio
async def test_render_web_table_content_none(mocker: MockerFixture):
    mocker.patch(READ_CSV, side_effect=FileNotFoundError("any"))
    template_spy = mocker.spy(Jinja2Templates, "TemplateResponse")
    response = await app_request(data.TABLE_URL)
    context: dict = template_spy.call_args_list[0].args[3]

    assert response.status_code == 200 and response.text
    assert data.HTML_CONTENT_TYPE in response.headers.items()
    assert not context["content"]
