from typing import Annotated

from fastapi import Depends, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.routing import APIRouter

from app.adapters.factories.usecase_factory import make_usecase
from app.adapters.presenters.template_context import TemplateContextBuilder
from app.core.data.dtos import SearchParams
from app.framework.dependencies import AccessToken, QueryParams
from app.framework.fastapi.config import SEARCH_ROUTE_DESCRIPTION, TEMPLATES

router = APIRouter(prefix="/scopus-survey/api")


@router.get(
    "/search-articles",
    status_code=200,
    tags=["API"],
    summary="Downloads the CSV file of found articles",
    response_description="CSV file of found articles downloaded",
    description=SEARCH_ROUTE_DESCRIPTION,
    response_class=FileResponse,
    dependencies=[Depends(AccessToken())],
)
async def search_articles(
    query_params: Annotated[QueryParams, Depends(QueryParams())]
):
    search_params = SearchParams.model_validate(query_params.to_dict())
    return make_usecase().get_articles(search_params)


@router.get(
    "",
    status_code=200,
    tags=["Web"],
    summary="Renders the application API web page",
    response_description="application API web page loaded",
    response_class=HTMLResponse,
)
async def render_web_application(request: Request):
    context = TemplateContextBuilder(request).get_web_app_context()
    return TEMPLATES.TemplateResponse(*context)


@router.get(
    "/table",
    status_code=200,
    tags=["Web"],
    summary="Renders the articles table web page",
    response_description="articles table web page loaded",
    response_class=HTMLResponse,
)
async def render_web_table(request: Request):
    context = TemplateContextBuilder(request).get_table_context()
    return TEMPLATES.TemplateResponse(*context)
