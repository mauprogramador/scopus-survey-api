from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.routing import APIRouter

from app.core.config.config import CSV_RESPONSE, HTML_RESPONSE, LOG
from app.core.data.query import APIKeyParam, CSVParams, SearchParams
from app.core.domain.factory import make_usecase
from app.adapters.helpers.template_builder import TemplateBuilder
from app.adapters.presenters.csv_response import CSVResponse
from app.core.data.enums import Language


router = APIRouter(prefix="/v2/scopus-survey/api")


@router.get(
    "/survey",
    status_code=HTTPStatus.OK,
    tags=["API"],
    summary="Survey for articles and download the found ones in a CSV file",
    responses=CSV_RESPONSE,
    response_class=FileResponse,
)
async def survey_articles(
    params: Annotated[SearchParams, Depends()]
) -> FileResponse:
    LOG.debug(vars(params))
    return make_usecase().retrieve_articles(params)


@router.get(
    "/csv",
    status_code=HTTPStatus.OK,
    tags=["API"],
    summary="Download the pre-existing CSV file of the found articles",
    responses=CSV_RESPONSE,
    response_class=FileResponse,
)
async def download_csv(
    params: Annotated[CSVParams, Depends()]
) -> FileResponse:
    LOG.debug(vars(params))
    return CSVResponse.build(params.api_key)


@router.get(
    "/{lang}/search-articles",
    status_code=HTTPStatus.OK,
    tags=["Web"],
    summary="Renders the search articles web page",
    responses=HTML_RESPONSE,
    response_class=HTMLResponse,
)
async def render_search_articles_page(
    request: Request, lang: Language
) -> HTMLResponse:
    LOG.debug({"search_page_lang": lang})
    return TemplateBuilder.search_template(request, lang)


@router.get(
    "/{lang}/articles-table",
    status_code=HTTPStatus.OK,
    tags=["Web"],
    summary="Renders the articles table web page",
    responses=HTML_RESPONSE,
    response_class=HTMLResponse,
)
async def render_articles_table_page(
    request: Request,
    lang: Language,
    params: Annotated[APIKeyParam, Depends()],
) -> HTMLResponse:
    LOG.debug({"table_page_lang": lang, "api_key": params.api_key})
    return TemplateBuilder.table_template(request, lang, params.api_key)
