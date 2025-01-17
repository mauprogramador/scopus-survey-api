from datetime import datetime
from http import HTTPStatus
from os.path import join

from pandas import read_csv
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

from app.core.config.scopus import (
    AUTHORS_COLUMN,
    DATE_COLUMN,
    TITLE_COLUMN,
    URL_COLUMN,
)
from app.core.data.enums import Language, Templates
from app.core.config.config import FILE, TOKEN, DIRECTORY
from app.core.domain.interfaces import TemplateBuilderABC
from app import __version__


class TemplateBuilder(TemplateBuilderABC):
    """Generates context values for template responses"""

    __COLUMNS = [URL_COLUMN, AUTHORS_COLUMN, TITLE_COLUMN, DATE_COLUMN]
    __SEARCH_ROUTE = "/scopus-survey/api/en-US/search-articles"
    __REDIRECT_HEADER = {
        "Location": __SEARCH_ROUTE,
        "Refresh": f"5; {__SEARCH_ROUTE}",
    }
    __TEMPLATES = Jinja2Templates(directory="web/templates")
    __ENCODING = "utf-8"
    __SEP = ";"

    @classmethod
    def search_template(cls, request: Request, lang: Language) -> HTMLResponse:
        template_name = f"{lang.value}/{Templates.SEARCH.value}"
        request.session.setdefault("csrf_token", TOKEN)
        headers = {"Content-Language": lang.value}
        context = {
            "version": __version__,
            "token": str(TOKEN),
            "lang": lang.value,
        }

        return cls.__TEMPLATES.TemplateResponse(
            request, template_name, context, HTTPStatus.OK, headers
        )

    @classmethod
    def table_template(
        cls, request: Request, lang: Language, api_key: str
    ) -> HTMLResponse:
        template_name = f"{lang.value}/{Templates.TABLE.value}"
        headers = {"Content-Language": lang.value}
        filename = f"{api_key}_{FILE}"

        try:
            file_path = join(DIRECTORY, filename)

            dataframe = read_csv(
                filepath_or_buffer=file_path,
                sep=cls.__SEP,
                usecols=cls.__COLUMNS,
                encoding=cls.__ENCODING,
            )

            # subset = dataframe[cls.__COLUMNS]
            csv_data = dataframe.to_numpy().tolist()

        except FileNotFoundError:
            csv_data = None

        context = {
            "version": __version__,
            "csv_filename": filename,
            "csv_data": csv_data,
            "lang": lang.value,
        }

        return cls.__TEMPLATES.TemplateResponse(
            request, template_name, context, HTTPStatus.OK, headers
        )

    @classmethod
    def not_found_template(
        cls, request: Request, response: Response, message: str
    ) -> HTMLResponse:
        template_name = Templates.ERROR.value
        code = response.status_code
        context = {
            "message": message,
            "status": f"{code} - {HTTPStatus(code).phrase}",
            "timestamp": datetime.now().isoformat(),
        }
        return cls.__TEMPLATES.TemplateResponse(
            request,
            template_name,
            context,
            HTTPStatus.OK,
            cls.__REDIRECT_HEADER,
        )
