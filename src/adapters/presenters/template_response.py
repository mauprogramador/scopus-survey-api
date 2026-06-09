from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path

import jinja2
from fastapi.requests import Request as FastAPIRequest
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response as StarletteResponse

from src import __contact__, __version__
from src.adapters.presenters.json_response import ErrorJSON
from src.core.common.types import Translations
from src.core.config.config import MAX_AGE, META_INFO, PREFIX
from src.core.data.enums import ExcMsg, Lang


_ERROR_PAGE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
    "Content-Language": Lang.EN_US,
}

_TEMPLATES_DIR = Path("web/templates")
_DIST_DIR = Path("web/templates/dist")
_DIST = Path("dist")

_INDEX_EN_FILENAME = f"index_{Lang.EN_US.locale}.html.jinja"
_INDEX_PT_FILENAME = f"index_{Lang.PT_BR.locale}.html.jinja"

_INDEX_FILENAMES = {
    Lang.EN_US: (_DIST_DIR / _INDEX_EN_FILENAME),
    Lang.PT_BR: (_DIST_DIR / _INDEX_PT_FILENAME),
}
_INDEX_DIST_FILENAMES = {
    Lang.EN_US: str(_DIST / _INDEX_EN_FILENAME),
    Lang.PT_BR: str(_DIST / _INDEX_PT_FILENAME),
}

_TEMPLATES = Jinja2Templates(directory=_TEMPLATES_DIR)


def _dummy_url_for(name: str, **path_params) -> str:
    if path_params:
        kwargs = [f"{key}='{value}'" for key, value in path_params.items()]
        return f"{{{{url_for('{name}', {', '.join(kwargs)})}}}}"
    return f"{{{{url_for('{name}')}}}}"


def build_all_templates(web: Translations, meta: Translations) -> None:
    _DIST_DIR.mkdir(exist_ok=True)

    env = jinja2.Environment(
        autoescape=jinja2.select_autoescape(
            disabled_extensions=[".html.jinja"]
        ),
        loader=jinja2.FileSystemLoader(_TEMPLATES_DIR),
    )
    template = env.get_template("index.html.jinja")

    for lang in Lang:
        context = {
            "version": __version__,
            "email": __contact__,
            "prefix": PREFIX,
            "lang": lang.value,
            "_t": web[lang].gettext,
            "_m": meta[lang].gettext,
            "url_for": _dummy_url_for,
        }
        context.update(META_INFO)

        shell_html = template.render(**context)

        filename = _INDEX_FILENAMES[lang]
        with open(filename, "w", encoding="utf-8") as file:
            file.write(shell_html)


def get_web_form_template(
    request: FastAPIRequest, csrf_token: str, lang: Lang
) -> HTMLResponse:

    headers = {
        "Content-Language": lang.value,
        "X-CSRF-Token": csrf_token,
        "Cache-Control": f"public, max-age={MAX_AGE}, must-revalidate",
        "Content-Type": "text/html; charset=utf-8",
    }

    return _TEMPLATES.TemplateResponse(
        request,
        _INDEX_DIST_FILENAMES[lang],
        {"csrf_token": csrf_token},
        HTTPStatus.OK,
        headers,
    )


def get_not_found_template(
    request: FastAPIRequest, res: StarletteResponse | ErrorJSON
) -> HTMLResponse:

    context = {
        "prefix": PREFIX,
        "message": ExcMsg.UNEXPECTED_ERROR,
        "status_code": res.status_code,
        "status": HTTPStatus(res.status_code).phrase,
        "timestamp": datetime.now(timezone.utc).isoformat(
            timespec="seconds"  # e.g. 2026-01-01T00:00:00Z
        ),
        "error_json": res.body.decode(),  # type: ignore
    }

    return _TEMPLATES.TemplateResponse(
        request,
        "error.html.jinja",
        context,
        res.status_code,
        _ERROR_PAGE_HEADERS,
    )
