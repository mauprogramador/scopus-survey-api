from gettext import GNUTranslations, translation
from unittest.mock import MagicMock

from pytest import fixture, mark, raises
from pytest_mock import MockerFixture as Mocker

from src.core.data.enums import ExcMsg, Lang
from src.core.domain.translations import (
    _ERRORS,
    load_translations,
    translate_error,
)
from tests.mocks.errors import (
    HTTP_ERROR,
    SCOPUS_API_ERROR,
    STARLETTE_HTTP_EXCEPTION,
)
from tests.mocks.helpers import Patch
from tests.mocks.raw import REQUEST


TRANSLATIONS = Patch(load_translations, translation)
_TRANSLATIONS = {
    "starlette.unexpected_error": "any",
    "starlette.default": "any",
    "scopus.500.any": "any",
    "scopus.500": "any",
    "scopus.default": "any",
    "api.unexpected_error": "any",
    "api.default": "any",
}


def test_load_translationss():
    _ERRORS.clear()
    assert not _ERRORS
    web, meta = load_translations()
    assert _ERRORS[Lang.EN_US] and _ERRORS[Lang.PT_BR]
    assert web is not None and meta is not None
    assert web[Lang.EN_US] and web[Lang.PT_BR]
    assert meta[Lang.EN_US] and meta[Lang.PT_BR]


def test_error_load_translationss(mocker: Mocker):
    mocker.patch(**TRANSLATIONS(FileNotFoundError("any")))
    with raises(FileNotFoundError) as info:
        load_translations()
    assert info.value.args[0] == "any"


@fixture(scope="module", name="trans")
def translate_error_fixture():

    def _mock_gettext(key: str) -> str:
        return _TRANSLATIONS[key]

    _ERRORS[Lang.EN_US] = MagicMock(GNUTranslations, gettext=_mock_gettext)
    yield


@mark.usefixtures("trans")
def test_translate_error():
    assert translate_error(REQUEST, STARLETTE_HTTP_EXCEPTION) == "any"
    _TRANSLATIONS["starlette.unexpected_error"] = "starlette.unexpected_error"

    assert translate_error(REQUEST, STARLETTE_HTTP_EXCEPTION) == "any"
    _TRANSLATIONS["starlette.default"] = "starlette.default"

    exc_msg = ExcMsg.UNEXPECTED_ERROR
    assert translate_error(REQUEST, STARLETTE_HTTP_EXCEPTION) == exc_msg


@mark.usefixtures("trans")
def test_translate_scopus_api_error():
    assert translate_error(REQUEST, SCOPUS_API_ERROR) == "any"
    _TRANSLATIONS["scopus.500.any"] = "scopus.500.any"

    assert translate_error(REQUEST, SCOPUS_API_ERROR) == "any"
    _TRANSLATIONS["scopus.500"] = "scopus.500"

    assert translate_error(REQUEST, SCOPUS_API_ERROR) == "any"
    _TRANSLATIONS["scopus.default"] = "scopus.default"

    exc_msg = ExcMsg.UNEXPECTED_ERROR
    assert translate_error(REQUEST, SCOPUS_API_ERROR) == exc_msg


@mark.usefixtures("trans")
def test_translate_http_error():
    assert translate_error(REQUEST, HTTP_ERROR) == "any"
    _TRANSLATIONS["api.unexpected_error"] = "api.unexpected_error"

    assert translate_error(REQUEST, HTTP_ERROR) == "any"
    _TRANSLATIONS["api.default"] = "api.default"

    exc_msg = ExcMsg.UNEXPECTED_ERROR
    assert translate_error(REQUEST, HTTP_ERROR) == exc_msg
