from fastapi.templating import Jinja2Templates
from pytest import raises
from pytest_mock import MockerFixture as Mocker

from src.adapters.presenters.error_response import ErrorJSON
from src.adapters.presenters.html_response import TemplateBuilder
from src.core.common.error_messages import UNEXPECTED_ERROR
from src.core.data.enums import Lang
from tests.mocks.helpers import fqn
from tests.mocks.raw import CSRF_TOKEN, HTML_MEDIA, HTTP_200, HTTP_404, REQUEST


def test_load_translations():
    translations = "_TemplateBuilder__TRANSLATIONS"
    assert hasattr(TemplateBuilder, translations)
    assert getattr(TemplateBuilder, translations)[Lang.EN_US]
    assert getattr(TemplateBuilder, translations)[Lang.PT_BR]


def test_error_load_translations(mocker: Mocker):
    target = fqn(TemplateBuilder.load_translations)
    mocker.patch(target, side_effect=FileNotFoundError("any"))
    with raises(FileNotFoundError) as info:
        TemplateBuilder.load_translations()
    assert info.value.args[0] == "any"


def test_search_template(mocker: Mocker):
    spy_jinja = mocker.spy(Jinja2Templates, "TemplateResponse")
    TemplateBuilder.load_translations()
    res = TemplateBuilder.search_template(REQUEST, CSRF_TOKEN, Lang.EN_US)

    assert res.status_code == HTTP_200
    assert res.media_type == HTML_MEDIA and res.body
    assert res.headers["Content-Language"] == Lang.EN_US
    assert res.headers["X-CSRF-Token"] == CSRF_TOKEN
    assert res.headers["Cache-Control"]
    assert res.headers["Content-Type"]

    context: dict = spy_jinja.call_args_list[0].args[3]
    assert context["version"] and context["prefix"]
    assert context["csrf_token"] == CSRF_TOKEN
    assert context["lang"] == Lang.EN_US


def test_not_found_template(mocker: Mocker):
    spy_jinja = mocker.spy(Jinja2Templates, "TemplateResponse")
    error_json = ErrorJSON(REQUEST, HTTP_404, "any")
    res = TemplateBuilder.not_found_template(REQUEST, error_json)

    assert res.status_code == HTTP_404
    assert res.media_type == HTML_MEDIA and res.body
    assert res.headers["Content-Language"] == Lang.EN_US
    assert res.headers["Cache-Control"]
    assert res.headers["Pragma"] == "no-cache"
    assert res.headers["Expires"] == "0"

    context: dict = spy_jinja.call_args_list[0].args[3]
    assert context["status"] and context["prefix"] and context["timestamp"]
    assert context["status_code"] == HTTP_404
    assert context["message"] == UNEXPECTED_ERROR
    assert context["error_json"]
