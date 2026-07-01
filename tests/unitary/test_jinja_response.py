import shutil

import jinja2
from fastapi.templating import Jinja2Templates
from pytest_mock import MockerFixture as Mocker

from src.adapters.presenters.jinja_response import (
    _DIST_DIR,
    _INDEX_FILENAMES,
    build_all_templates,
    get_not_found_template,
    get_web_form_template,
)
from src.adapters.presenters.json_response import ErrorJSON
from src.core.config.config import META_INFO
from src.core.data.enums import ExcMsg, Lang
from src.core.domain.translations import load_translations
from tests.mocks.raw import CSRF_TOKEN, HTML_MEDIA, HTTP_200, HTTP_404, REQUEST


def test_build_all(mocker: Mocker):
    if _DIST_DIR.exists():
        shutil.rmtree(_DIST_DIR)
    _DIST_DIR.mkdir()

    spy_jinja = mocker.spy(jinja2.Template, "render")
    build_all_templates(*load_translations())

    assert _DIST_DIR.exists()
    assert _INDEX_FILENAMES[Lang.EN_US].exists()
    assert _INDEX_FILENAMES[Lang.PT_BR].exists()

    assert spy_jinja.call_count == 2
    ctx = spy_jinja.call_args_list[0].kwargs
    assert ctx["version"] and ctx["email"] and ctx["prefix"]
    assert ctx["lang"] == Lang.EN_US
    assert ctx["_t"] and ctx["_m"]
    assert META_INFO.items() <= ctx.items()


def test_form_template(mocker: Mocker):
    spy_jinja = mocker.spy(Jinja2Templates, "TemplateResponse")
    res = get_web_form_template(REQUEST, CSRF_TOKEN, Lang.EN_US)

    assert res.status_code == HTTP_200
    assert res.media_type == HTML_MEDIA and res.body
    assert res.headers["Content-Language"] == Lang.EN_US
    assert res.headers["X-CSRF-Token"] == CSRF_TOKEN
    assert res.headers["Cache-Control"]
    assert res.headers["Content-Type"]

    ctx: dict = spy_jinja.call_args_list[0].args[3]
    assert ctx["csrf_token"] == CSRF_TOKEN


def test_not_found_template(mocker: Mocker):
    spy_jinja = mocker.spy(Jinja2Templates, "TemplateResponse")
    error_json = ErrorJSON(REQUEST, HTTP_404, "any", "any")
    res = get_not_found_template(REQUEST, error_json)

    assert res.status_code == HTTP_404
    assert res.media_type == HTML_MEDIA and res.body
    assert res.headers["Content-Language"] == Lang.EN_US
    assert res.headers["Cache-Control"]
    assert res.headers["Pragma"] == "no-cache"
    assert res.headers["Expires"] == "0"

    ctx: dict = spy_jinja.call_args_list[0].args[3]
    assert ctx["status"] and ctx["prefix"] and ctx["timestamp"]
    assert ctx["status_code"] == HTTP_404
    assert ctx["message"] == ExcMsg.INTERNAL_ERROR
    assert ctx["error_json"]
