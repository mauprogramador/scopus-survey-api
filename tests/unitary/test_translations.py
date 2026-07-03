import gettext
from unittest.mock import MagicMock, Mock

from pytest import fixture, mark, raises
from pytest_mock import MockerFixture as Mocker

from src.core.data.enums import ExcMsg, Lang
from src.core.domain.translations import (
    _ERRORS,
    _get_lang,
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


TRANSLATIONS = Patch(load_translations, gettext.translation, "gettext")
_TRANSLATIONS = {
    "starlette.unexpected_error": "any",
    "starlette.default": "any",
    "scopus.500.any": "any",
    "scopus.500": "any",
    "scopus.default": "any",
    "api.internal_error": "any",
    "api.default": "any",
}


def test_load_translations():
    _ERRORS.clear()
    assert not _ERRORS
    web, meta = load_translations()
    assert _ERRORS[Lang.EN_US] and _ERRORS[Lang.PT_BR]
    assert web is not None and meta is not None
    assert web[Lang.EN_US] and web[Lang.PT_BR]
    assert meta[Lang.EN_US] and meta[Lang.PT_BR]


def test_error_load_translations(mocker: Mocker):
    mocker.patch(**TRANSLATIONS(FileNotFoundError("any")))
    with raises(FileNotFoundError) as info:
        load_translations()
    assert info.value.args[0] == "any"


@fixture(scope="module", name="mock_gettext")
def translate_error_fixture():

    def _mock_gettext(key: str) -> str:
        return _TRANSLATIONS[key]

    _ERRORS[Lang.EN_US] = MagicMock(
        gettext.GNUTranslations, gettext=_mock_gettext
    )
    yield


@mark.usefixtures("mock_gettext")
def test_translate_error():
    assert translate_error(REQUEST, STARLETTE_HTTP_EXCEPTION) == "any"
    _TRANSLATIONS["starlette.unexpected_error"] = "starlette.unexpected_error"

    assert translate_error(REQUEST, STARLETTE_HTTP_EXCEPTION) == "any"
    _TRANSLATIONS["starlette.default"] = "starlette.default"

    exc_msg = ExcMsg.INTERNAL_ERROR
    assert translate_error(REQUEST, STARLETTE_HTTP_EXCEPTION) == exc_msg


@mark.usefixtures("mock_gettext")
def test_translate_scopus_api_error():
    assert translate_error(REQUEST, SCOPUS_API_ERROR) == "any"
    _TRANSLATIONS["scopus.500.any"] = "scopus.500.any"

    assert translate_error(REQUEST, SCOPUS_API_ERROR) == "any"
    _TRANSLATIONS["scopus.500"] = "scopus.500"

    assert translate_error(REQUEST, SCOPUS_API_ERROR) == "any"
    _TRANSLATIONS["scopus.default"] = "scopus.default"

    exc_msg = ExcMsg.INTERNAL_ERROR
    assert translate_error(REQUEST, SCOPUS_API_ERROR) == exc_msg


@mark.usefixtures("mock_gettext")
def test_translate_http_error():
    assert translate_error(REQUEST, HTTP_ERROR) == "any"
    _TRANSLATIONS["api.internal_error"] = "api.internal_error"

    assert translate_error(REQUEST, HTTP_ERROR) == "any"
    _TRANSLATIONS["api.default"] = "api.default"

    exc_msg = ExcMsg.INTERNAL_ERROR
    assert translate_error(REQUEST, HTTP_ERROR) == exc_msg


@mark.parametrize(
    "accept_lang,expected_lang",
    [
        (None, Lang.EN_US),
        ("en-US", Lang.EN_US),
        ("pt-BR", Lang.PT_BR),
        ("en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7", Lang.EN_US),
        ("en;q=0.9,pt-BR;q=0.8,pt;q=0.7", Lang.EN_US),
        ("pt-BR;q=0.8,pt;q=0.7", Lang.PT_BR),
        ("pt;q=0.7", Lang.PT_BR),
        ("en-GB;q=0.7", Lang.EN_US),
        ("en", Lang.EN_US),
        ("pt", Lang.PT_BR),
        ("fr", Lang.EN_US),
        ("fr-FR;q=0.8,fr;q=0.7", Lang.EN_US),
    ],
)
def test_get_lang(accept_lang: str | None, expected_lang: Lang):
    req = Mock(headers={"Accept-Language": accept_lang})
    assert _get_lang(req) == expected_lang
