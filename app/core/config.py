from datetime import datetime
from re import compile as compile_pattern
from tempfile import mkdtemp
from uuid import uuid4

from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import Example
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

TEMPLATES = Jinja2Templates(directory='app/web/templates')

STATIC = {
    '/styles': StaticFiles(directory='app/web/static/css'),
    '/icons': StaticFiles(directory='app/web/static/icon'),
    '/images': StaticFiles(directory='app/web/static/img'),
    '/scripts': StaticFiles(directory='app/web/static/js'),
    '/svgs': StaticFiles(directory='app/web/static/svg'),
}


DIRECTORY = mkdtemp()
CURRENT_YEAR = datetime.now().year
TOKEN = str(uuid4().hex)


DESCRIPTION = (
    'The value of the X-Access-Token header will be '
    'set automatically, you **should not** change it'
)
OPENAPI_EXAMPLE = {
    'Token': Example(
        summary='Access Token', description=DESCRIPTION, value=TOKEN
    )
}


# Match: no spaces, only letters and numbers; length of exactly 32.
API_KEY_PATTERN = r'^[a-zA-Z0-9]{32}$'

# Match: letters, numbers, spaces and underscores; length between 2 and 120.
KEYWORD_PATTERN = compile_pattern(r'^[a-zA-Z0-9_ ]{2,120}$')

# Match: two or more consecutive spaces.
SPACES_PATTERN = r' {2,}'

# Match: no spaces, only letters and numbers; length of exactly 32.
TOKEN_PATTERN = r'^[a-zA-Z0-9]{32}$'


CORS = {
    'middleware_class': CORSMiddleware,
    'allow_origins': ['*'],
    'allow_credentials': True,
    'allow_methods': ['GET'],
    'allow_headers': ['*'],
}
