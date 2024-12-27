from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.routing import APIRouter

from app.adapters.factories.usecase_factory import make_usecase
from app.adapters.helpers.template_builder import TemplateBuilder
from app.adapters.presenters.csv_response import CSVResponse
from app.core.data.enums import Language
from app.core.data.validators import SearchParams
from app.framework.dependencies import AccessToken, SearchQueryParams
from app.framework.dependencies.api_key_query_param import APIKeyQueryParam
from app.framework.fastapi.config import SEARCH_ROUTE_DESCRIPTION


router = APIRouter(prefix="/scopus-survey/api")


@router.get(
    "/survey",
    status_code=HTTPStatus.OK,
    tags=["API"],
    summary="Survey for articles and download the found ones in a CSV file",
    response_description="CSV file of found articles downloaded",
    description=SEARCH_ROUTE_DESCRIPTION,
    response_class=FileResponse,
    dependencies=[Depends(AccessToken())],
)
async def survey_articles(
    query_params: Annotated[SearchQueryParams, Depends(SearchQueryParams())]
):
    search_params = SearchParams.model_validate(query_params.items)
    return make_usecase().get_articles(search_params)


@router.get(
    "/csv",
    status_code=HTTPStatus.OK,
    tags=["API"],
    summary="Download the pre-existing CSV file of the found articles",
    response_description="CSV file of found articles downloaded",
    response_class=FileResponse,
    dependencies=[Depends(AccessToken())],
)
async def download_csv(
    api_key: Annotated[str, Depends(APIKeyQueryParam())],
):
    return CSVResponse.build(api_key)


@router.get(
    "/{lang}/search-articles",
    status_code=HTTPStatus.OK,
    tags=["Web"],
    summary="Renders the search articles web page",
    response_description="search articles web page loaded",
    response_class=HTMLResponse,
)
async def render_search_articles_web_page(
    request: Request,
    lang: Language,
):
    return TemplateBuilder.search_template(request, lang)


@router.get(
    "/{lang}/articles-table",
    status_code=HTTPStatus.OK,
    tags=["Web"],
    summary="Renders the articles table web page",
    response_description="articles table web page loaded",
    response_class=HTMLResponse,
)
async def render_articles_table_web_page(
    request: Request,
    lang: Language,
    api_key: Annotated[str, Depends(APIKeyQueryParam())],
):
    return TemplateBuilder.table_template(request, lang, api_key)
