from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import Example
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import TOKEN, TOML
from app.framework.exceptions.handle_exceptions import (
    BaseExceptionResponse,
    ExceptionHandler,
)
from app.framework.fastapi.lifespan import lifespan

TITLE = 'Scopus-Searcher-API'
VERSION = 'v2.0.0'
SUMMARY = 'API for Bibliographic Survey of Scopus Articles'
DESCRIPTION = f"""
[**Web Application**]({TOML.url}/scopus-searcher/api)
&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
[**Documentation**](https://mauprogramador.github.io/scopus-searcher-api/)
"""

SEARCH_ROUTE_DESCRIPTION = """
**Keywords:** must be separated by a comma and each keyword can contain
letters, numbers, underscores and spaces, from 2 to 120 characters <br/><br/>
**Ex.:** Python, Machine Learning, Data Science, Neural Networks
"""
WEB_API_ROUTE_DESCRIPTION = f"""
**Web API:** <{TOML.url}/scopus-searcher/api>
"""
WEB_TABLE_ROUTE_DESCRIPTION = f"""
**Web Table:** <{TOML.url}/scopus-searcher/api/table>
"""

RESPONSES = {
    422: {
        'model': BaseExceptionResponse,
        'description': 'Base Exception Response',
    }
}
CONTACT = {
    'name': 'Mauricio',
    'email': 'mauricio.batista@estudante.ifms.edu.br',
}
FASTAPI = {
    'title': TITLE,
    'summary': SUMMARY,
    'description': DESCRIPTION,
    'version': VERSION,
    'docs_url': '/',
    'responses': RESPONSES,
    'contact': CONTACT,
    'exception_handlers': ExceptionHandler().handlers,
    'lifespan': lifespan,
}
TEMPLATES = Jinja2Templates(directory='app/framework/web/templates')
STATIC_PATH = 'app/framework/web/static'
STATIC = {
    '/styles': StaticFiles(directory=f'{STATIC_PATH}/css'),
    '/icons': StaticFiles(directory=f'{STATIC_PATH}/icon'),
    '/images': StaticFiles(directory=f'{STATIC_PATH}/img'),
    '/scripts': StaticFiles(directory=f'{STATIC_PATH}/js'),
    '/svgs': StaticFiles(directory=f'{STATIC_PATH}/svg'),
}
DESCRIPTION = (
    'The value of the X-Access-Token header will be '
    'set automatically, you **should not** change it'
)
OPENAPI_EXAMPLE = {
    'Token': Example(
        summary='Access Token', description=DESCRIPTION, value=TOKEN
    )
}
CORS = {
    'middleware_class': CORSMiddleware,
    'allow_origins': ['*'],
    'allow_credentials': True,
    'allow_methods': ['GET'],
    'allow_headers': ['*'],
}
