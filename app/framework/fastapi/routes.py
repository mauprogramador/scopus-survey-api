from typing import Annotated

from fastapi import Depends, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.routing import APIRouter

from app.adapters.presenters.csv_table import LoadCSVData
from app.core.config import TOKEN
from app.core.usecase import Scopus
from app.framework.dependencies import AccessToken, QueryParams
from app.framework.fastapi.config import (
    SEARCH_ROUTE_DESCRIPTION,
    TEMPLATES,
    WEB_API_ROUTE_DESCRIPTION,
    WEB_TABLE_ROUTE_DESCRIPTION,
)

router = APIRouter(prefix='/scopus-searcher/api')


@router.get(
    '/search-articles',
    status_code=200,
    tags=['API'],
    summary='Searches Scopus Articles',
    response_description='Articles found',
    description=SEARCH_ROUTE_DESCRIPTION,
    response_class=FileResponse,
    dependencies=[Depends(AccessToken())],
)
async def search_articles(
    query_params: Annotated[QueryParams, Depends(QueryParams)]
):
    return Scopus().search_articles(query_params)


@router.get(
    '',
    status_code=200,
    tags=['Web'],
    summary='Render Web API Interface',
    response_description='Web API Interface loaded',
    description=WEB_API_ROUTE_DESCRIPTION,
    response_class=HTMLResponse,
)
async def render_web_application(request: Request):
    context = {'request': request, 'token': TOKEN}
    return TEMPLATES.TemplateResponse(request, 'index.html', context)


@router.get(
    '/table',
    status_code=200,
    tags=['Web'],
    summary='Render Web CSV Table',
    response_description='Web CSV Table Interface loaded',
    description=WEB_TABLE_ROUTE_DESCRIPTION,
    response_class=HTMLResponse,
)
async def render_web_table(request: Request):
    data = LoadCSVData().handle()
    context = {'request': request, 'content': data}
    return TEMPLATES.TemplateResponse(request, 'table.html', context)
