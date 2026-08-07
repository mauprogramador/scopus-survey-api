import gettext
from pathlib import Path

from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.requests import Request as FastAPIRequest
from pydantic_core import ValidationError
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.adapters.types import Translations
from src.core.domain.types import ExcMsg, Lang
from src.core.domain.exceptions import HTTPError, ScopusAPIError
from src.infra.utils import logger


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
            languages=[Lang.EN_US.snake_case],
        )
        meta[Lang.EN_US] = gettext.translation(
            domain=_META_DOMAIN,
            localedir=_LOCALEDIR,
            languages=[Lang.EN_US.snake_case],
        )
        _ERRORS[Lang.EN_US] = gettext.translation(
            domain=_ERROR_DOMAIN,
            localedir=_LOCALEDIR,
            languages=[Lang.EN_US.snake_case],
        )

        web[Lang.PT_BR] = gettext.translation(
            domain=_WEB_DOMAIN,
            localedir=_LOCALEDIR,
            languages=[Lang.PT_BR.snake_case],
        )
        meta[Lang.PT_BR] = gettext.translation(
            domain=_META_DOMAIN,
            localedir=_LOCALEDIR,
            languages=[Lang.PT_BR.snake_case],
        )
        _ERRORS[Lang.PT_BR] = gettext.translation(
            domain=_ERROR_DOMAIN,
            localedir=_LOCALEDIR,
            languages=[Lang.PT_BR.snake_case],
        )

        return web, meta

    except (FileNotFoundError, OSError) as exc:
        logger.error("Error loading translations")
        raise exc


_LANG_CODE_MAP = {
    Lang.EN_US.lower(): Lang.EN_US,
    Lang.EN_US.snake_case: Lang.EN_US,
    Lang.EN_US.snake_case.lower(): Lang.EN_US,
    Lang.EN_US.short: Lang.EN_US,
    Lang.PT_BR.lower(): Lang.PT_BR,
    Lang.PT_BR.snake_case: Lang.PT_BR,
    Lang.PT_BR.snake_case.lower(): Lang.PT_BR,
    Lang.PT_BR.short: Lang.PT_BR,
}


def _get_lang(request: FastAPIRequest) -> Lang:
    accept_lang = request.headers.get("Accept-Language")

    if not accept_lang:
        return Lang.EN_US

    if accept_lang in Lang:
        return Lang(accept_lang)

    for part in accept_lang.split(","):
        lang = part.strip().split(";", maxsplit=1)[0]

        if not lang:
            continue

        if lang in Lang:
            return Lang(lang)

        if lang in _LANG_CODE_MAP:
            return _LANG_CODE_MAP[lang]

        base_lang = lang.split("-", maxsplit=1)[0]
        if base_lang in _LANG_CODE_MAP:
            return _LANG_CODE_MAP[base_lang]

    return Lang.EN_US


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

    lang = _get_lang(request)

    if isinstance(exc, ScopusAPIError):
        status_code = str(exc.details[0]["status_code"])
        error_code = exc.details[0]["error_code"]
        suffixes = (f"{status_code}.{error_code}", status_code, "default")

    elif isinstance(exc, HTTPError):
        suffixes = (exc.message.name.lower(), "default")

    for suffix in suffixes:
        key = f"{prefix}.{suffix}".lower()
        message = _ERRORS[lang].gettext(key)

        if message != key:
            return message

    logger.error("No translation found")
    return ExcMsg.INTERNAL_ERROR
