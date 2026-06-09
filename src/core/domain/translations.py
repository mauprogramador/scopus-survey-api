import gettext
from pathlib import Path

from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.requests import Request as FastAPIRequest
from pydantic_core import ValidationError
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.common.types import Translations
from src.core.data.enums import ExcMsg, Lang
from src.core.domain.http_exceptions import HTTPError, ScopusAPIError
from src.utils import logger


_LOCALEDIR = Path("locales")
_ERRORS: Translations = {}
_ERROR_DOMAIN = "error"
_META_DOMAIN = "meta"
_WEB_DOMAIN = "web"


def load_translations() -> tuple[Translations, Translations]:
    meta: Translations = {}
    web: Translations = {}

    try:
        web[Lang.EN_US] = gettext.translation(
            domain=_WEB_DOMAIN,
            localedir=_LOCALEDIR,
            languages=[Lang.EN_US.locale],
        )
        meta[Lang.EN_US] = gettext.translation(
            domain=_META_DOMAIN,
            localedir=_LOCALEDIR,
            languages=[Lang.EN_US.locale],
        )
        _ERRORS[Lang.EN_US] = gettext.translation(
            domain=_ERROR_DOMAIN,
            localedir=_LOCALEDIR,
            languages=[Lang.EN_US.locale],
        )

        web[Lang.PT_BR] = gettext.translation(
            domain=_WEB_DOMAIN,
            localedir=_LOCALEDIR,
            languages=[Lang.PT_BR.locale],
        )
        meta[Lang.PT_BR] = gettext.translation(
            domain=_META_DOMAIN,
            localedir=_LOCALEDIR,
            languages=[Lang.PT_BR.locale],
        )
        _ERRORS[Lang.PT_BR] = gettext.translation(
            domain=_ERROR_DOMAIN,
            localedir=_LOCALEDIR,
            languages=[Lang.PT_BR.locale],
        )

        return web, meta

    except (FileNotFoundError, OSError) as exc:
        logger.error("Error loading translations")
        raise exc


_PREFIXES = {
    HTTPError: ("api", ""),
    ScopusAPIError: ("scopus", ""),
    StarletteHTTPException: ("starlette", "unexpected_error"),
    FastAPIHTTPException: ("starlette", "unexpected_error"),
    RequestValidationError: ("fastapi", "request_validation_error"),
    ResponseValidationError: ("fastapi", "response_validation_error"),
    ValidationError: ("pydantic", "validation_error"),
    RateLimitExceeded: ("slowapi", ExcMsg.SLOWAPI_RATE_ERROR.name),
}


def translate_error(request: FastAPIRequest, exc: Exception) -> str:
    if type(exc) in _PREFIXES:
        prefix, suffix = _PREFIXES[type(exc)]
        suffixes = (suffix, "default")

    else:
        for handler_exc, handler_data in _PREFIXES.items():
            if issubclass(type(exc), handler_exc):
                prefix, suffix = handler_data
                suffixes = (suffix, "default")
                break

    lang = request.headers.get("Accept-Language", Lang.EN_US)
    _e = _ERRORS[Lang(lang)].gettext

    if isinstance(exc, ScopusAPIError):
        status_code = str(exc.details[0]["status_code"])
        error_code = exc.details[0]["error_code"]
        suffixes = (f"{status_code}.{error_code}", status_code, "default")

    elif isinstance(exc, HTTPError):
        suffixes = (exc.message.name.lower(), "default")

    for suffix in suffixes:
        key = f"{prefix}.{suffix}".lower()
        message = _e(key)

        if message != key:
            return message

    logger.error("No translation found")
    return ExcMsg.UNEXPECTED_ERROR
