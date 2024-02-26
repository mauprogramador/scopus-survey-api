from fastapi.responses import FileResponse

from app.dependencies import QueryParams
from tests.data.models import Article, FakeResponse


def get_csv_file(tmpdir) -> FileResponse:
    with open(f'{tmpdir}/articles.csv', 'w', encoding='utf-8') as file:
        file.write('Any')
    return FileResponse(f'{tmpdir}/articles.csv')


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

BASE_URL = 'http://127.0.0.1:8000/scopus-searcher/api'
API_KEY = '6bd9327547a3cf4c56586324df4b7d92'
KEYWORDS = ['Python', 'Machine Learning']
QUERY_PARAMS = f"?apikey={API_KEY}&keywords={','.join(KEYWORDS)}"
SEARCH_ARTICLES_URL = f'{BASE_URL}/search-articles'
URL = f'{BASE_URL}/search-articles{QUERY_PARAMS}'
API_KEY_URL = f'{SEARCH_ARTICLES_URL}?apikey='
KEYWORDS_URL = f'{API_KEY_URL}{API_KEY}&keywords='
CSV_CONTENT_TYPE = ('content-type', 'text/csv; charset=utf-8')
HTML_CONTENT_TYPE = ('content-type', 'text/html; charset=utf-8')


SESSION_SEND = 'requests.sessions.Session.send'
HTTP_HELPER_REQUEST = 'app.gateway.http_helper.HttpHelper.make_request'
BASE_SCOPUS_API = 'app.gateway.scopus_api.ScopusApi'
SCOPUS_API_SEARCH_ARTICLES = f'{BASE_SCOPUS_API}.search_articles'
SCOPUS_API_SCRAPING_ARTICLE = f'{BASE_SCOPUS_API}.scraping_article'
SEARCH_ARTICLES = 'app.core.usecase.Scopus.search_articles'


FAKE_API_URL = 'https://jsonplaceholder.typicode.com/users/1'
FAKE_SEARCH_ARTICLES_200 = FakeResponse(
    {'search-results': {'opensearch:totalResults': 1, 'entry': True}}
)
FAKE_HTTP_HELPER_REQUEST = {
    400: FakeResponse(None, 400),
    401: FakeResponse(None, 401),
    403: FakeResponse(None, 403),
    404: FakeResponse(None, 404),
    429: FakeResponse(None, 429),
    500: FakeResponse(None, 500),
}
FAKE_SEARCH_ARTICLES_DECODING_ERROR = FakeResponse('any')
FAKE_SEARCH_ARTICLES_EMPTY_CONTENT = FakeResponse('{}')
FAKE_SEARCH_ARTICLES_NOT_FOUND = FakeResponse(
    {'search-results': {'opensearch:totalResults': 0, 'entry': True}}
)
FAKE_SCRAPING_ARTICLE_200 = FakeResponse('<html></html>')
FAKE_SCOPUS_ID = 'SCOPUS:123'
FAKE_ARTICLE_ID = '123'
FAKE_SCRAPING_ARTICLE_EMPTY_CONTENT = FakeResponse('')
FAKE_API_PARAMS = QueryParams(api_key=API_KEY, keywords=KEYWORDS)
FAKE_SCOPUS_API_SEARCH_ARTICLES = [Article().model_dump(by_alias=True)]
FAKE_SCOPUS_API_SCRAPING_ARTICLE = tuple(
    ['https://scopus.com.br/article/any_page.html', TEMPLATE]
)
FAKE_DUPLICATES_ARTICLES = [
    FAKE_SCOPUS_API_SEARCH_ARTICLES[0],
    FAKE_SCOPUS_API_SEARCH_ARTICLES[0],
    Article(
        url='http://123.org',
        scopus_id='SCOPUS_ID:85137995725',
        title='any_title_2',
        publication_name='2015',
        volume='415',
        date='2015',
        doi='10.15.100/15-10',
        citations='15',
    ).model_dump(by_alias=True),
    Article(
        url='http://456.org',
        scopus_id='SCOPUS_ID:85137995726',
        title='any_title_2',
        publication_name='2016',
        volume='416',
        date='2016',
        doi='10.16.100/16-10',
        citations='16',
    ).model_dump(by_alias=True),
]
FAKE_ARTICLE = FakeResponse(TEMPLATE)


CONNECTION_TIMEOUT = 'Request Connection Timeout'
CONNECTION_ERROR = 'Connection Error in Request'
CONNECTION_EXCEPTION = 'Unexpected Error from Request: any'
INVALID_ARTICLE_PAGE = 'Invalid Response from Article Page'
VALIDATION_ERROR = 'Validation error in request/response'
INVALID_RESPONSE = 'Invalid Response from Scopus API'
DECODING_ERROR = 'Error in decoding response from Scopus API'
NOT_FOUND = 'None articles has been found'
MISSING_API_KEY = 'Missing ApiKey required query parameter'
MISSING_KEYWORDS = 'Missing keywords required query parameter'
INVALID_KEYWORD = 'Invalid keyword'
INVALID_MINIMUM_LENGTH_KEYWORDS = 'There must be at least two keywords'
MISSING_ACCESS_TOKEN = 'No access token provided'
INVALID_ACCESS_TOKEN = 'Invalid access token'
INVALID_SHORT_VALUE = 'String should have at least 32 characters'
INVALID_LONG_VALUE = 'String should have at most 32 characters'
INVALID_PATTERN = "String should match pattern '^[a-zA-Z0-9]{32}$'"
