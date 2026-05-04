from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.responses import Response

from src import __contact__, __version__
from src.adapters.presenters.json_response import ErrorJSON
from src.core.common.error_messages import UNEXPECTED_ERROR
from src.core.config.config import MAX_AGE, META_INFO, PREFIX
from src.core.data.enums import Lang
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
    def _dummy_url_for(cls, name: str, **path_params) -> str:
        if path_params:
            kwargs = [f"{key}='{value}'" for key, value in path_params.items()]
            return f"{{{{url_for('{name}', {', '.join(kwargs)})}}}}"
        return f"{{{{url_for('{name}')}}}}"

    @classmethod
    def build_all(cls) -> None:
        dist_dir = Path("web/templates/dist")
        dist_dir.mkdir(exist_ok=True)

        env = Environment(
            autoescape=select_autoescape(disabled_extensions=[".html.jinja"]),
            loader=FileSystemLoader(cls.TEMPLATES_DIR),
        )
        template = env.get_template("index.html.jinja")

        for lang in Lang:
            context = {
                "version": __version__,
                "email": __contact__,
                "prefix": PREFIX,
                "lang": lang.value,
                "_t": Translations.WEB[lang].gettext,
                "_m": Translations.META[lang].gettext,
                "url_for": cls._dummy_url_for,
            }
            context.update(META_INFO)

            shell_html = template.render(**context)

            filename = dist_dir / f"index_{lang.locale}.html"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(shell_html)

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

        return cls._TEMPLATES.TemplateResponse(
            request,
            f"dist/index_{lang.locale}.html",
            {"csrf_token": csrf_token},
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
            "error.html",
            context,
            response.status_code,
            cls._ERROR_PAGE_HEADERS,
        )
