from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

from src import __version__
from src.adapters.presenters.json_response import ErrorJSON
from src.core.common.error_messages import UNEXPECTED_ERROR
from src.core.config.config import MAX_AGE, PREFIX
from src.core.data.enums import Lang, Templates
from src.core.domain.translations import Translations


class TemplateResponse:
    """Generates context values for template responses"""

    _ERROR_PAGE_HEADERS = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
        "Content-Language": Lang.EN_US,
    }
    _TEMPLATES = Jinja2Templates(directory="web/templates")

    @classmethod
    def form_template(
        cls, request: Request, csrf_token: str, lang: Lang
    ) -> HTMLResponse:

        headers = {
            "Content-Language": lang.value,
            "X-CSRF-Token": csrf_token,
            "Cache-Control": f"public, max-age={MAX_AGE}, must-revalidate",
            "Content-Type": "text/html; charset=utf-8",
        }

        context = {
            "version": __version__,
            "prefix": PREFIX,
            "csrf_token": csrf_token,
            "lang": lang.value,
            "_t": Translations.WEB[lang].gettext,
            "_m": Translations.META[lang].gettext,
            "_e": Translations.ERROR[lang].gettext,
        }

        return cls._TEMPLATES.TemplateResponse(
            request,
            Templates.INDEX.value,
            context,
            HTTPStatus.OK,
            headers,
        )

    @classmethod
    def not_found_template(
        cls, request: Request, response: Response | ErrorJSON
    ) -> HTMLResponse:

        context = {
            "prefix": PREFIX,
            "message": UNEXPECTED_ERROR,
            "status_code": response.status_code,
            "status": HTTPStatus(response.status_code).phrase,
            "timestamp": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
            "error_json": response.body.decode(),  # type: ignore
        }

        return cls._TEMPLATES.TemplateResponse(
            request,
            Templates.ERROR.value,
            context,
            response.status_code,
            cls._ERROR_PAGE_HEADERS,
        )
