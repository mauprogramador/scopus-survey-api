import shutil

import jinja2
from fastapi.templating import Jinja2Templates
from pytest_mock import MockerFixture as Mocker

from src.adapters.presenters.json_response import ErrorJSON
from src.adapters.presenters.template_response import TemplateResponse
from src.core.config.config import META_INFO
from src.core.data.enums import ExcMsg, Lang
from src.core.domain.translations import load_translations
from tests.mocks.raw import CSRF_TOKEN, HTML_MEDIA, HTTP_200, HTTP_404, REQUEST


def test_build_all(mocker: Mocker):
    if TemplateResponse.DIST_DIR.exists():
        shutil.rmtree(TemplateResponse.DIST_DIR)
    TemplateResponse.DIST_DIR.mkdir()

    spy_jinja = mocker.spy(jinja2.Template, "render")
    translations = load_translations()
    TemplateResponse.build_all(*translations)

    assert TemplateResponse.DIST_DIR.exists()
    assert TemplateResponse.INDEX_FILENAMES[Lang.EN_US].exists()
    assert TemplateResponse.INDEX_FILENAMES[Lang.PT_BR].exists()

    assert spy_jinja.call_count == 2
    context = spy_jinja.call_args_list[0].kwargs
    assert context["version"] and context["email"] and context["prefix"]
    assert context["lang"] == Lang.EN_US
    assert context["_t"] and context["_m"]
    assert META_INFO.items() <= context.items()


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
    assert context["csrf_token"] == CSRF_TOKEN


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
    assert context["message"] == ExcMsg.UNEXPECTED_ERROR
    assert context["error_json"]
