from datetime import datetime
from http import HTTPStatus
from json import load

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src import __version__
from src.adapters.presenters.error_response import ErrorJSON
from src.core.common.error_messages import UNEXPECTED_ERROR
from src.core.common.types import Translation
from src.core.config.config import LOG, MAX_AGE, PREFIX
from src.core.data.enums import Lang, Templates


class TemplateBuilder:
    """Generates context values for template responses"""

    __TRANSLATIONS: Translation = {}
    __REDIRECT_HEADER = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
        "Content-Language": Lang.EN_US,
    }
    __TEMPLATES = Jinja2Templates(directory="web/templates")

    @classmethod
    def load_translations(cls) -> None:
        try:
            path = "web/static/lang/en_us.json"
            with open(path, "r", encoding="utf-8") as file:
                cls.__TRANSLATIONS.setdefault(Lang.EN_US, load(file))

            path = "web/static/lang/pt_br.json"
            with open(path, "r", encoding="utf-8") as file:
                cls.__TRANSLATIONS.setdefault(Lang.PT_BR, load(file))

        except Exception as exc:
            LOG.error("Error loading translations")
            raise exc

    @classmethod
    def search_template(
        cls, request: Request, csrf_token: str, lang: Lang
    ) -> HTMLResponse:

        request.session["csrf-token"] = csrf_token
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
        }
        context.update(cls.__TRANSLATIONS[lang])

        return cls.__TEMPLATES.TemplateResponse(
            request,
            Templates.INDEX.value,
            context,
            HTTPStatus.OK,
            headers,
        )

    @classmethod
    def not_found_template(
        cls, request: Request, response: ErrorJSON
    ) -> HTMLResponse:

        context = {
            "prefix": PREFIX,
            "message": UNEXPECTED_ERROR,
            "status_code": response.status_code,
            "status": HTTPStatus(response.status_code).phrase,
            "timestamp": datetime.now().isoformat(),
            "error_json": response.body.decode(),  # type: ignore
        }

        return cls.__TEMPLATES.TemplateResponse(
            request,
            Templates.ERROR.value,
            context,
            response.status_code,
            cls.__REDIRECT_HEADER,
        )
