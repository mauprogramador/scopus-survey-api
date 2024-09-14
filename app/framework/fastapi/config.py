from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import Example
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config.config import TOKEN, TOKEN_HEADER, TOML_ENV
from app.framework.exceptions.exception_handler import ExceptionHandler
from app.framework.exceptions.http_exceptions import BaseExceptionResponse
from app.framework.fastapi.lifespan import lifespan

SEARCH_ROUTE_DESCRIPTION = """
**Keywords:** must be separated by a comma and each keyword can contain
letters, numbers, underscores and spaces, from 2 to 50 characters <br/><br/>
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
    f"The value of the {TOKEN_HEADER} header will be "
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
