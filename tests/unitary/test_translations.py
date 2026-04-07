from gettext import translation

from pytest import raises
from pytest_mock import MockerFixture as Mocker

from src.core.data.enums import Lang
from src.core.domain.translations import Translations
from tests.mocks.helpers import fqn


def test_load_all():
    assert Translations.WEB and Translations.META and Translations.ERROR
    assert Translations.WEB[Lang.EN_US] and Translations.WEB[Lang.PT_BR]
    assert Translations.META[Lang.EN_US] and Translations.META[Lang.PT_BR]
    assert Translations.ERROR[Lang.EN_US] and Translations.ERROR[Lang.PT_BR]


def test_error_load_all(mocker: Mocker):
    Translations.load_all.cache_clear()
    target = fqn(Translations, translation)
    mocker.patch(target, side_effect=FileNotFoundError("any"))
    with raises(FileNotFoundError) as info:
        Translations.load_all()
    assert info.value.args[0] == "any"
