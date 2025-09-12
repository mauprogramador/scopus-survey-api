from gettext import GNUTranslations, translation
from pathlib import Path

from src.core.config.config import LOG
from src.core.data.enums import Lang


class Translations:
    """Loads and stores translations"""

    _LOCALEDIR = Path("web/locales")
    _ERROR_DOMAIN = "error"
    _WEB_DOMAIN = "web"

    ERROR: dict[Lang, GNUTranslations] = {}
    WEB: dict[Lang, GNUTranslations] = {}

    @classmethod
    def load_all(cls) -> None:
        try:
            cls.WEB[Lang.EN_US] = translation(
                domain=cls._WEB_DOMAIN,
                localedir=cls._LOCALEDIR,
                languages=[Lang.EN_US.locale],
            )
            cls.ERROR[Lang.EN_US] = translation(
                domain=cls._ERROR_DOMAIN,
                localedir=cls._LOCALEDIR,
                languages=[Lang.EN_US.locale],
            )

            cls.WEB[Lang.PT_BR] = translation(
                domain=cls._WEB_DOMAIN,
                localedir=cls._LOCALEDIR,
                languages=[Lang.PT_BR.locale],
            )
            cls.ERROR[Lang.PT_BR] = translation(
                domain=cls._ERROR_DOMAIN,
                localedir=cls._LOCALEDIR,
                languages=[Lang.PT_BR.locale],
            )

        except (FileNotFoundError, OSError) as exc:
            LOG.error("Error loading translations")
            raise exc
