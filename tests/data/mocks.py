from pydantic_core import InitErrorDetails
from requests.exceptions import Timeout

from app.core.config import TOML
from app.framework.dependencies import QueryParams
from tests.data.models import Article, FakeResponse
from tests.data.utils import get_api_response, load_groups

BASE_URL = f'{TOML.url}/scopus-searcher/api'
API_KEY = '6bd9327547a3cf4c56586324df4b7d92'
KEYWORDS = ['Python', 'Machine Learning']
QUERY_PARAMS = f"?apikey={API_KEY}&keywords={','.join(KEYWORDS)}"
SEARCH_ARTICLES_URL = f'{BASE_URL}/search-articles'
URL = f'{BASE_URL}/search-articles{QUERY_PARAMS}'
API_KEY_URL = f'{SEARCH_ARTICLES_URL}?apikey='
KEYWORDS_URL = f'{API_KEY_URL}{API_KEY}&keywords='
CSV_CONTENT_TYPE = ('content-type', 'text/csv; charset=utf-8')
HTML_CONTENT_TYPE = ('content-type', 'text/html; charset=utf-8')
TABLE_URL = f'{BASE_URL}/table'

SESSION_SEND = 'requests.sessions.Session.send'
HELPER_PATH = 'app.adapters.helpers.http_helper'
HTTP_HELPER_REQUEST = f'{HELPER_PATH}.HttpHelper.make_request'
BASE_SCOPUS_API = 'app.adapters.gateway.scopus_api.ScopusApi'
SCOPUS_API_SEARCH_ARTICLES = f'{BASE_SCOPUS_API}.search_articles'
SCOPUS_API_SCRAPING_ARTICLE = f'{BASE_SCOPUS_API}.scraping_article'
SEARCH_ARTICLES = 'app.core.usecase.Scopus.search_articles'
RENAME_DATAFRAME = 'pandas.core.frame.DataFrame.rename'
RANGE = f'{HELPER_PATH}.range'
SLEEP = f'{HELPER_PATH}.sleep'
CSV_TABLE = 'app.adapters.presenters.csv_table.LoadCSVData.handle'
READ_CSV = 'app.adapters.presenters.csv_table.read_csv'

TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>Article Page</title>
    </head>
    <body>
        <section id="authorlist">
        <ul class="list-inline">
            <li><span class="previewTxt">Any1, A.</span></li>
            <li><span class="previewTxt">Any2, B.</span></li>
        </ul>
        </section>
        <section id="abstractSection">
            <p>Any abstract that will describe the article</p>
        </section>
    </body>
    </html>
"""

SCOPUS_RESPONSE_JSON = {
    'search-results': {
        'opensearch:totalResults': 156,
        'opensearch:itemsPerPage': 25,
        'entry': [],
    },
}

FAKE_HTTP_RESPONSES = {
    400: FakeResponse(None, 400),
    401: FakeResponse(None, 401),
    403: FakeResponse(None, 403),
    404: FakeResponse(None, 404),
    429: FakeResponse(None, 429),
    500: FakeResponse(None, 500),
}

FAKE_LINK = 'https://jsonplaceholder.typicode.com/users/1'
FAKE_ARTICLES = [Article().model_dump(by_alias=True)]
FAKE_TEMPLATE = FakeResponse(TEMPLATE)
FAKE_API_PARAMS = QueryParams(api_key=API_KEY, keywords=KEYWORDS)
FAKE_SCOPUS_API_SCRAPING_ARTICLE = (FAKE_LINK, TEMPLATE)

FAKE_RESPONSE_FOUND = get_api_response('1', [{'any': 'any'}])
FAKE_RESPONSE_PAGINATION = [
    get_api_response('32', [{'A': 'any'}]),
    get_api_response('32', [{'B': 'any'}]),
]
FAKE_RESPONSE_NOT_FOUND = get_api_response('0', [])
FAKE_RESPONSE_200 = get_api_response('1', FAKE_ARTICLES)
FAKE_RESPONSE_NO_CONTENT = get_api_response('None')
FAKE_RESPONSE_DECODING_200 = FakeResponse('')

FAKE_CSV_DATA = [['any'], ['any']]
FAKE_LINE_ERRORS = [InitErrorDetails(type='missing', input='any')]
FAKE_RETRY = [Timeout(), Timeout(), FAKE_RESPONSE_200]
FAKE_ABSTRACT = 'Any abstract that will describe the article'
FAKE_AUTHORS = 'Any1 A., Any2 B.'

FAKE_DUPLICATES_ARTICLES = [
    FAKE_ARTICLES[0],
    FAKE_ARTICLES[0],
    Article(title='any_title_2', doi='123').model_dump(by_alias=True),
    Article(title='any_title_2', doi='456').model_dump(by_alias=True),
]
FAKE_DUPLICATE_AUTHORS_ARTICLES = [
    Article(title='any_title_2').model_dump(by_alias=True),
    Article(title='any_title_3').model_dump(by_alias=True),
]
FAKE_DATA_NO_GROUP = load_groups(['lorem', 'any'])
FAKE_DATA_ONE_GROUP = load_groups({'lorem': 1, 'any': 2})
FAKE_DATA_GROUPS = load_groups({'lorem': 1, 'any': 2, 'commodo': 3})

CONNECTION_EXCEPTION = 'Unexpected Error from Request: any'
CONNECTION_STATUS_ERROR = 'Unexpected status error'
CONNECTION_TIMEOUT = 'Request Connection Timeout'
CONNECTION_ERROR = 'Connection Error in Request'
DECODING_ERROR = 'Error in decoding response from Scopus API'
VALIDATION_ERROR = 'Validation error in request/response'
NOT_FOUND = 'None articles has been found'
INVALID_MINIMUM_LENGTH_KEYWORDS = 'There must be at least two keywords'
INVALID_PATTERN = "String should match pattern '^[a-zA-Z0-9]{32}$'"
INVALID_SHORT_VALUE = 'String should have at least 32 characters'
INVALID_LONG_VALUE = 'String should have at most 32 characters'
INVALID_RESPONSE = 'Invalid Response from Scopus API'
INVALID_ACCESS_TOKEN = 'Invalid access token'
INVALID_KEYWORD = 'Invalid keyword'
MISSING_KEYWORDS = 'Missing keywords required query parameter'
MISSING_API_KEY = 'Missing ApiKey required query parameter'
MISSING_ACCESS_TOKEN = 'No access token provided'
