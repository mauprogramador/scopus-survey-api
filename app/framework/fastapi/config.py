from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import Example
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config.config import TOKEN, TOKEN_HEADER, TOML_ENV
from app.framework.exceptions.exception_handler import ExceptionHandler
from app.framework.exceptions.http_exceptions import BaseExceptionResponse
from app.framework.fastapi.lifespan import lifespan

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

DESCRIPTION = f"""
[**Web Application**](/scopus-searcher/api)
&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
[**Documentation**]({TOML_ENV.documentation})
"""

CONTACT = {
    "name": TOML_ENV.name,
    "url": "https://github.com/mauprogramador",
    "email": TOML_ENV.email,
}
LICENSE = {
    "name": "MIT License",
    "identifier": "MIT",
    "url": (
        "https://github.com/mauprogramador/"
        "scopus-searcher-api/blob/master/LICENSE"
    ),
}
RESPONSES = {
    400: {
        "model": BaseExceptionResponse,
        "description": "Base exceptions response",
    }
}
FASTAPI = {
    "debug": TOML_ENV.debug,
    "title": TOML_ENV.title,
    "summary": TOML_ENV.description,
    "description": DESCRIPTION,
    "version": f"v{TOML_ENV.version}",
    "docs_url": "/",
    "exception_handlers": ExceptionHandler().handlers,
    "lifespan": lifespan,
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
}
