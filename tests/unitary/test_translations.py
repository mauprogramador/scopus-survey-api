from gettext import translation

from pytest import raises
from pytest_mock import MockerFixture as Mocker

from src.core.data.enums import Lang
from src.core.domain.translations import Translations
from tests.mocks.helpers import Patch


TRANSLATIONS = Patch(Translations, translation)


def test_load_all():
    Translations.ERROR = {}
    assert not Translations.ERROR
    web, meta = Translations.load_all()
    assert Translations.ERROR[Lang.EN_US] and Translations.ERROR[Lang.PT_BR]
    assert web is not None and meta is not None
    assert web[Lang.EN_US] and web[Lang.PT_BR]
    assert meta[Lang.EN_US] and meta[Lang.PT_BR]


def test_error_load_all(mocker: Mocker):
    mocker.patch(**TRANSLATIONS(FileNotFoundError("any")))
    with raises(FileNotFoundError) as info:
        Translations.load_all()
    assert info.value.args[0] == "any"
