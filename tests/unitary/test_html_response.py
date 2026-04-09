from fastapi.templating import Jinja2Templates
from pytest_mock import MockerFixture as Mocker

from src.adapters.presenters.json_response import ErrorJSON
from src.adapters.presenters.template_response import TemplateResponse
from src.core.common.error_messages import UNEXPECTED_ERROR
from src.core.config.config import META_INFO
from src.core.data.enums import Lang
from tests.mocks.raw import CSRF_TOKEN, HTML_MEDIA, HTTP_200, HTTP_404, REQUEST


def test_form_template(mocker: Mocker):
    spy_jinja = mocker.spy(Jinja2Templates, "TemplateResponse")
    res = TemplateResponse.form_template(REQUEST, CSRF_TOKEN, Lang.EN_US)

    assert res.status_code == HTTP_200
    assert res.media_type == HTML_MEDIA and res.body
    assert res.headers["Content-Language"] == Lang.EN_US
    assert res.headers["X-CSRF-Token"] == CSRF_TOKEN
    assert res.headers["Cache-Control"]
    assert res.headers["Content-Type"]

    context: dict = spy_jinja.call_args_list[0].args[3]
    assert context["version"] and context["email"] and context["prefix"]
    assert context["csrf_token"] == CSRF_TOKEN
    assert context["lang"] == Lang.EN_US
    assert context["_t"] and context["_m"] and context["_e"]
    assert META_INFO.items() <= context.items()


def test_not_found_template(mocker: Mocker):
    spy_jinja = mocker.spy(Jinja2Templates, "TemplateResponse")
    error_json = ErrorJSON(REQUEST, HTTP_404, "any")
    res = TemplateResponse.not_found_template(REQUEST, error_json)

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
