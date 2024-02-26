from typing import Annotated

from fastapi import Depends, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.routing import APIRouter

from app.api.swagger import ROUTE_DESCRIPTION
from app.core.config import TEMPLATES, TOKEN
from app.core.usecase import Scopus
from app.dependencies import AccessToken, QueryParams

router = APIRouter(prefix='/scopus-searcher/api', tags=['API'])


@router.get(
    '/search-articles',
    status_code=200,
    summary='Searches Scopus Articles',
    response_description='Articles found',
    description=ROUTE_DESCRIPTION,
    response_class=FileResponse,
    dependencies=[Depends(AccessToken())],
)
async def search_articles(
    query_params: Annotated[QueryParams, Depends(QueryParams)]
):
    return Scopus.search_articles(query_params)


@router.get(
    '',
    status_code=200,
    summary='Render Web API Interface',
    response_description='Web API Interface loaded',
    response_class=HTMLResponse,
)
async def render_template(request: Request):
    context = {'request': request, 'token': TOKEN}
    return TEMPLATES.TemplateResponse(request, 'index.html', context)
