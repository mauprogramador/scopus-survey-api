from http import HTTPStatus
from typing import Annotated

from fastapi import Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.routing import APIRouter

from src.adapters.presenters.csv_response import CSVResponse
from src.adapters.presenters.html_response import TemplateBuilder
from src.core.config.config import LIMIT, LIMITER, LOG, MAX_AGE, PREFIX
from src.core.data.enums import Lang
from src.core.data.query_params import (
    CombinationParams,
    CSVParams,
    SearchParams,
)
from src.core.domain.factory import make_usecase
from src.framework.fastapi.csrf_token import CSRFToken
from src.framework.fastapi.swagger import (
    CSV_RESPONSE,
    HTML_RESPONSE,
    JSON_RESPONSE,
)

router = APIRouter(prefix=PREFIX)


@router.get(
    "/web/{lang}/search-articles",
    status_code=HTTPStatus.OK,
    tags=["Web"],
    summary="Renders the search articles web page",
    responses=HTML_RESPONSE,
    response_class=HTMLResponse,
)
async def render_search_articles_page(
    request: Request,
    lang: Lang,
) -> HTMLResponse:
    csrf_token, signed_token = CSRFToken.generate_csrf_tokens()
    LOG.debug(
        {
            "search_page_lang": lang,
            "csrf_token": csrf_token,
            "signed_token": signed_token,
        }
    )
    response = TemplateBuilder.search_template(request, csrf_token, lang)
    response.set_cookie("csrf-token", signed_token, MAX_AGE, httponly=True)
    return response


@router.get(
    "/api/combination",
    status_code=HTTPStatus.OK,
    tags=["API"],
    summary="",
    responses=JSON_RESPONSE,
    response_class=JSONResponse,
)
@LIMITER.limit(LIMIT)
async def survey_keywords_combination(
    request: Request,
    params: Annotated[CombinationParams, Query()],
) -> JSONResponse:
    LOG.debug(params.model_dump())
    CSRFToken.verify_csrf_token(request, params.csrf_token)

    return JSONResponse(
        {
            "combinations": [
                {"keyword": "Python", "total": 110000},
                {"keyword": "AI", "total": 500000},
                {"keyword": "Python AND AI", "total": 50000},
            ]
        }
    )


@router.get(
    "/api/survey",
    status_code=HTTPStatus.OK,
    tags=["API"],
    summary="Survey for articles and download the found ones in a CSV file",
    responses=CSV_RESPONSE,
    response_class=FileResponse,
)
@LIMITER.limit(LIMIT)
async def survey_articles(
    request: Request,
    params: Annotated[SearchParams, Query()],
) -> FileResponse:
    LOG.debug(params.model_dump())
    CSRFToken.verify_csrf_token(request, params.csrf_token)
    response = make_usecase().retrieve_articles(params)
    return response


@router.get(
    "/api/csv",
    status_code=HTTPStatus.OK,
    tags=["API"],
    summary="Download the pre-existing CSV file of the found articles",
    responses=CSV_RESPONSE,
    response_class=FileResponse,
)
@LIMITER.limit(LIMIT)
async def download_csv(
    request: Request,
    params: Annotated[CSVParams, Query()],
) -> FileResponse:
    LOG.debug(params.model_dump())
    CSRFToken.verify_csrf_token(request, params.csrf_token)
    response = CSVResponse.build(params.api_key)
    return response
