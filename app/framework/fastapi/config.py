from http import HTTPStatus
from secrets import token_hex

from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import Example
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ratelimit import RateLimitMiddleware, Rule
from ratelimit.backends.simple import MemoryBackend
from ratelimit.auths.session import from_session
from starlette.middleware.sessions import SessionMiddleware

from app.core.config.config import (
    CSV_HEADER,
    TOKEN,
    TOKEN_HEADER,
    TOML_ENV,
    USER_API_KEY_HEADER,
)
from app.framework.exceptions.exception_handler import ExceptionHandler
from app.framework.exceptions.http_exceptions import BaseExceptionResponse


SEARCH_ROUTE_DESCRIPTION = """
### API Key
You must obtain one to access the <a
href="https://dev.elsevier.com/sc_apis.html" target="_blank" rel="external
help" title="Scopus APIs">Scopus APIs</a> to search and retrieve the articles'
information. It **has no spaces** and is **made up of 32 characters**
containing **only letters and numbers**. It can be obtained by accessing the
<a href="https://dev.elsevier.com/" target="_blank" rel="external help"
title="Elsevier Developer Portal">Elsevier Portal</a> and registering.
### Keywords
Based on the theme or subject of your research, you must select a **minimum
of two**, and a **maximum of four keywords**, which will be used as
parameters and filters when searching for articles. Each keyword must be
**written in English**, containing **only letters, numbers, spaces and
underscores**, with a **minimum of 2** and a **maximum of 50 characters**.

**Ex.:** Python, Machine Learning, Data Science, Neural Networks
"""

DESCRIPTION = """
[**Web Application**](/scopus-survey/api/en-US/search-articles)
&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
[**Documentation**](https://mauprogramador.github.io/scopus-survey-api/)
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

FASTAPI = {
    "debug": TOML_ENV.debug,
    "title": "ScopusSurveyAPI",
    "summary": "Web API for bibliographic survey of Scopus articles",
    "description": DESCRIPTION,
    "version": f"v{TOML_ENV.version}",
    "docs_url": "/",
    "exception_handlers": ExceptionHandler().handlers,
    "contact": CONTACT,
    "license_info": LICENSE,
    "responses": RESPONSES,
}

TEMPLATES = Jinja2Templates(directory="web/templates")
STATIC = {
    "/styles": StaticFiles(directory="web/static/css"),
    "/images": StaticFiles(directory="web/static/img"),
    "/scripts": StaticFiles(directory="web/static/js"),
    "/svgs": StaticFiles(directory="web/static/svg"),
    "/files": StaticFiles(directory="csv"),
}

DESCRIPTION = (
    f"The value of the `{TOKEN_HEADER}` header will be "
    "set automatically, you **should not** change it"
)
OPENAPI_EXAMPLE = {
    "Token": Example(
        summary="Access Token", description=DESCRIPTION, value=TOKEN
    )
}

CORS = {
    "middleware_class": CORSMiddleware,
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["GET"],
    "allow_headers": ["*"],
    "expose_headers": [CSV_HEADER, USER_API_KEY_HEADER],
}

TIME_RULE = Rule(method="get", second=30, block_time=10)
RATE_LIMIT = {
    "middleware_class": RateLimitMiddleware,
    "authenticate": from_session,
    "backend": MemoryBackend(),
    "config": {
        r"^/scopus-survey/api/survey": [TIME_RULE],
        r"^/scopus-survey/api/csv": [TIME_RULE],
    },
}

SESSION = {
    "middleware_class": SessionMiddleware,
    "secret_key": token_hex(nbytes=16),
    "max_age": None,
}
