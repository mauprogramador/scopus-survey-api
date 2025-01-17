from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from ratelimit import RateLimitMiddleware, Rule
from ratelimit.backends.simple import MemoryBackend
from starlette.middleware.sessions import SessionMiddleware

from app.core.common.patterns import (
    CSV_ROUTE_PATTERN,
    SEARCH_ROUTE_PATTERN,
    SURVEY_ROUTE_PATTERN,
    TABLE_ROUTE_PATTERN,
)
from app.core.config.config import SECRET_KEY, ENV
from app.framework.fastapi.from_session import from_session
from app.framework.fastapi.routes import router
from app.framework.middleware import (
    RedirectNotFoundMiddleware,
    TracingTimeMiddleware,
    SecurityHeadersMiddleware,
    ExceptionHandlerMiddleware,
)
from app.core.domain.http_exceptions import BaseExceptionResponse
from app import __version__


DESCRIPTION = """
🌐 [**Web Application**](/v2/scopus-survey/api/en-US/search-articles)
&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
📄 [**Documentation**](https://mauprogramador.github.io/scopus-survey-api/)
"""
CONTACT = {
    "name": "@mauprogramador",
    "url": "https://github.com/mauprogramador",
    "email": "sir.silvabmauricio@gmail.com",
}
LICENSE = {
    "name": "MIT License",
    "identifier": "MIT",
    "url": (
        "https://github.com/mauprogramador/"
        "scopus-survey-api/blob/master/LICENSE"
    ),
}
RESPONSES = {
    HTTPStatus.BAD_REQUEST: {
        "model": BaseExceptionResponse,
        "description": "Base exceptions response",
    }
}

app = FastAPI(
    debug=ENV.debug,
    title="ScopusSurveyAPI",
    summary="Web API for bibliographic survey of Scopus articles",
    description=DESCRIPTION,
    version=f"v{__version__}",
    contact=CONTACT,
    license_info=LICENSE,
    responses=RESPONSES,
)

RULE = [
    Rule(group="default", method="get", second=3, minute=150, block_time=10)
]
app.add_middleware(
    RateLimitMiddleware,
    authenticate=from_session,
    backend=MemoryBackend(),
    config={
        SURVEY_ROUTE_PATTERN: RULE,
        CSV_ROUTE_PATTERN: RULE,
        SEARCH_ROUTE_PATTERN: RULE,
        TABLE_ROUTE_PATTERN: RULE,
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TracingTimeMiddleware)
app.add_middleware(RedirectNotFoundMiddleware)
app.add_middleware(ExceptionHandlerMiddleware)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=None,
)

app.mount("/styles", StaticFiles(directory="web/static/css"))
app.mount("/images", StaticFiles(directory="web/static/img"))
app.mount("/scripts", StaticFiles(directory="web/static/js"))
app.mount("/svgs", StaticFiles(directory="web/static/svg"))
app.mount("/files", StaticFiles(directory="csv"))


@app.get(
    "/",
    status_code=HTTPStatus.OK,
    tags=["Redirect"],
    summary="Redirects to home page",
    response_class=RedirectResponse,
)
async def read_root():
    url = "/v2/scopus-survey/api/en-US/search-articles"
    return RedirectResponse(url, HTTPStatus.SEE_OTHER)


app.include_router(router)
