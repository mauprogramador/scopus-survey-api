from http import HTTPStatus
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.routing import APIRouter

from src.adapters.presenters.csv_response import CSVResponse
from src.adapters.presenters.template_response import TemplateResponse
from src.core.config.config import LIMIT, LIMITER, LOG, MAX_AGE, PREFIX
from src.core.data.enums import Lang
from src.core.data.query_params import (
    CombinationParams,
    CSVParams,
    SearchParams,
)
from src.core.domain.factory import make_aggregator, make_combinator
from src.framework.fastapi.csrf_token import CSRFToken
from src.framework.fastapi.swagger import (
    CSV_RESPONSE,
    HTML_RESPONSE,
    JSON_RESPONSE,
)

favicon_router = APIRouter()
router = APIRouter(prefix=PREFIX)


@favicon_router.get(
    "/favicon.ico",
    status_code=HTTPStatus.OK,
    include_in_schema=False,
    response_class=FileResponse,
)
async def favicon():
    return FileResponse(
        path=Path("web/static/img/favicon.ico"),
        status_code=HTTPStatus.OK,
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": 'inline; filename="favicon.ico"',
        },
        media_type="image/x-icon",
        filename="favicon.ico",
    )


@router.get(
    "/web/{lang}/search-articles",
    status_code=HTTPStatus.OK,
    tags=["Web"],
    summary="Renders the search articles web page",
    responses=HTML_RESPONSE,
    response_class=HTMLResponse,
)
async def search_articles_page(
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

    request.session["csrf-token"] = csrf_token
    response = TemplateResponse.search_template(request, csrf_token, lang)
    response.set_cookie("csrf-token", signed_token, MAX_AGE, httponly=True)

    return response


@router.get(
    "/api/combination",
    status_code=HTTPStatus.OK,
    tags=["API"],
    dependencies=[Depends(CSRFToken.verify_csrf_token)],
    summary="",
    responses=JSON_RESPONSE,
    response_class=JSONResponse,
)
@LIMITER.limit(LIMIT)
async def survey_total_combinations(
    request: Request,  # pylint: disable=W0613
    params: Annotated[CombinationParams, Query()],
) -> JSONResponse:
    LOG.debug(params.model_dump())

    use_case = make_combinator()
    response = await use_case.survey_combinations(params)

    return response


@router.get(
    "/api/survey",
    status_code=HTTPStatus.OK,
    tags=["API"],
    dependencies=[Depends(CSRFToken.verify_csrf_token)],
    summary="Survey for articles and download the found ones in a CSV file",
    responses=CSV_RESPONSE,
    response_class=FileResponse,
)
@LIMITER.limit(LIMIT)
async def survey_articles(
    request: Request,  # pylint: disable=W0613
    params: Annotated[SearchParams, Query()],
) -> FileResponse:
    LOG.debug(params.model_dump())

    use_case = make_aggregator()
    response = await use_case.retrieve_articles(params)

    return response


@router.get(
    "/api/csv",
    status_code=HTTPStatus.OK,
    tags=["API"],
    dependencies=[Depends(CSRFToken.verify_csrf_token)],
    summary="Download the pre-existing CSV file of the found articles",
    responses=CSV_RESPONSE,
    response_class=FileResponse,
)
@LIMITER.limit(LIMIT)
async def download_csv(
    request: Request,  # pylint: disable=W0613
    params: Annotated[CSVParams, Query()],
) -> FileResponse:
    LOG.debug(params.model_dump())

    response = CSVResponse.build(params.api_key)

    return response
