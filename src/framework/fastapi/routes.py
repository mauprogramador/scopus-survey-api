from http import HTTPStatus
from typing import Annotated

import fastapi
from fastapi.requests import Request as FastAPIRequest
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.routing import APIRouter

from src.adapters.presenters.csv_response import CSVResponse
from src.adapters.presenters.template_response import TemplateResponse
from src.core.config.config import (
    FAVICON_HEADERS,
    FAVICON_PATH,
    LIMIT,
    LIMITER,
    MAX_AGE,
    PREFIX,
)
from src.core.data.enums import Lang
from src.core.data.query_params import (
    CombinationParams,
    CSVParams,
    SearchParams,
)
from src.core.domain.factory import make_aggregator, make_combinator
from src.framework.fastapi.csrf_token import CSRFToken
from src.framework.fastapi.swagger import (
    CSV_RESPONSES,
    JSON_RESPONSES,
    OPENAPI_EXTRA,
    ROUTE_DESCRIPTION,
    WEB_FORM_RESPONSES,
)
from src.utils import logger


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
        path=FAVICON_PATH,
        status_code=HTTPStatus.OK,
        headers=FAVICON_HEADERS,
        media_type="image/x-icon",
        filename="favicon.ico",
    )


@router.get(
    "/web/{lang}/survey-bibliographies",
    status_code=HTTPStatus.OK,
    tags=["Web"],
    summary="Renders the multi-step web form page",
    responses=WEB_FORM_RESPONSES,
    response_class=HTMLResponse,
)
async def web_form_page(
    request: FastAPIRequest,
    lang: Lang,
) -> HTMLResponse:

    csrf_token, signed_token = CSRFToken.generate_csrf_tokens()
    logger.debug(
        {
            "search_page_lang": lang,
            "csrf_token": csrf_token,
            "signed_token": signed_token,
        }
    )

    res = TemplateResponse.form_template(request, csrf_token, lang)
    res.set_cookie("csrf-token", signed_token, MAX_AGE, httponly=True)

    return res


@router.get(
    "/api/combination",
    status_code=HTTPStatus.OK,
    tags=["API"],
    dependencies=[fastapi.Depends(CSRFToken.verify_csrf_token)],
    summary="Survey the totals of keyword combinations",
    description=ROUTE_DESCRIPTION,
    responses=JSON_RESPONSES,
    response_class=JSONResponse,
    openapi_extra=OPENAPI_EXTRA,
)
@LIMITER.limit(LIMIT)
async def survey_total_combinations(
    request: FastAPIRequest,  # pylint: disable=W0613
    params: Annotated[CombinationParams, fastapi.Query()],
) -> JSONResponse:
    logger.debug(params.model_dump())

    use_case = make_combinator()
    res = await use_case.survey_combinations(params)

    return res


@router.get(
    "/api/survey",
    status_code=HTTPStatus.OK,
    tags=["API"],
    dependencies=[fastapi.Depends(CSRFToken.verify_csrf_token)],
    summary="Survey bibliographies and return the CSV file",
    description=ROUTE_DESCRIPTION,
    responses=CSV_RESPONSES,
    response_class=FileResponse,
    openapi_extra=OPENAPI_EXTRA,
)
@LIMITER.limit(LIMIT)
async def survey_bibliographic_data(
    request: FastAPIRequest,  # pylint: disable=W0613
    params: Annotated[SearchParams, fastapi.Query()],
) -> FileResponse:
    logger.debug(params.model_dump())

    use_case = make_aggregator()
    res = await use_case.retrieve_articles(params)

    return res


@router.get(
    "/api/csv",
    status_code=HTTPStatus.OK,
    tags=["API"],
    dependencies=[fastapi.Depends(CSRFToken.verify_csrf_token)],
    summary="Download the pre-existing CSV file",
    description=ROUTE_DESCRIPTION,
    responses=CSV_RESPONSES,
    response_class=FileResponse,
    openapi_extra=OPENAPI_EXTRA,
)
@LIMITER.limit(LIMIT)
async def download_csv(
    request: FastAPIRequest,  # pylint: disable=W0613
    params: Annotated[CSVParams, fastapi.Query()],
) -> FileResponse:
    logger.debug(params.model_dump())

    res = CSVResponse.retrieve(params.api_key)

    return res
