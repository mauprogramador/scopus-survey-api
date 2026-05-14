from gettext import translation
from pathlib import Path

from src.core.common.types import Trans
from src.core.config.config import LOG
from src.core.data.enums import Lang


class Translations:
    """Loads and stores translations"""

    _LOCALEDIR = Path("locales")
    _ERROR_DOMAIN = "error"
    _META_DOMAIN = "meta"
    _WEB_DOMAIN = "web"

    ERROR: Trans = {}

    @classmethod
    def load_all(cls) -> tuple[Trans, Trans]:
        meta: Trans = {}
        web: Trans = {}

        try:
            web[Lang.EN_US] = translation(
                domain=cls._WEB_DOMAIN,
                localedir=cls._LOCALEDIR,
                languages=[Lang.EN_US.locale],
            )
            meta[Lang.EN_US] = translation(
                domain=cls._META_DOMAIN,
                localedir=cls._LOCALEDIR,
                languages=[Lang.EN_US.locale],
            )
            cls.ERROR[Lang.EN_US] = translation(
                domain=cls._ERROR_DOMAIN,
                localedir=cls._LOCALEDIR,
                languages=[Lang.EN_US.locale],
            )

            web[Lang.PT_BR] = translation(
                domain=cls._WEB_DOMAIN,
                localedir=cls._LOCALEDIR,
                languages=[Lang.PT_BR.locale],
            )
            meta[Lang.PT_BR] = translation(
                domain=cls._META_DOMAIN,
                localedir=cls._LOCALEDIR,
                languages=[Lang.PT_BR.locale],
            )
            cls.ERROR[Lang.PT_BR] = translation(
                domain=cls._ERROR_DOMAIN,
                localedir=cls._LOCALEDIR,
                languages=[Lang.PT_BR.locale],
            )

            return web, meta

        except (FileNotFoundError, OSError) as exc:
            LOG.error("Error loading translations")
            raise exc
