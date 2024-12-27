from pytest_mock import MockerFixture

from app.adapters.helpers.template_builder import TemplateContextBuilder
from app.core.config.config import TOKEN
from tests.mocks.common import CSV_DATA
from tests.mocks.fixtures import READ_CSV
from tests.mocks.unitary import EMPTY_REQUEST


def test_web_app_context():
    context = TemplateContextBuilder().get_web_app_context()
    assert context[0] == EMPTY_REQUEST and context[1] == "index.html"
    assert len(context[2]) == 9
    assert context[2]["token"] == TOKEN


def test_table_context(mocker: MockerFixture):
    mocker.patch(READ_CSV, return_value=CSV_DATA)
    context = TemplateContextBuilder().get_table_context()
    assert context[0] == EMPTY_REQUEST and context[1] == "table.html"
    assert len(context[2]) == 6 and context[2]["content"]
    assert context[2]["content"] == CSV_DATA.to_numpy().tolist()


def test_table_context_none(mocker: MockerFixture):
    mocker.patch(READ_CSV, side_effect=FileNotFoundError("any"))
    context = TemplateContextBuilder().get_table_context()
    assert context[0] == EMPTY_REQUEST and context[1] == "table.html"
    assert len(context[2]) == 6 and context[2]["content"] is None
