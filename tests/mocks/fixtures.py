from threading import Event

from fastapi.exceptions import (
    HTTPException as FastAPIHTTPException,
    RequestValidationError,
    ResponseValidationError,
)
from pydantic_core import InitErrorDetails, ValidationError
from requests.sessions import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.adapters.gateway.scopus_articles_page import ScopusArticlesPage
from app.adapters.gateway.scopus_search_api import ScopusSearchAPI
from app.adapters.helpers.http_retry_helper import HTTPRetryHelper
from app.adapters.helpers.url_builder_helper import URLBuilderHelper
from app.adapters.presenters.template_context import TemplateContextBuilder
from app.core.domain.exceptions import ApplicationError, ScopusAPIError
from app.core.usecases import (
    ArticlesPageScraper,
    ArticlesSimilarityFilter,
    ScopusArticlesAggregator,
)
from app.framework.dependencies.access_token import AccessToken
from app.framework.dependencies.query_params import QueryParams
from app.framework.exceptions import HTTPException
from app.framework.exceptions.exception_handler import ExceptionHandler
from tests.helpers.models import MockArticlesScraper, MockSimilarityFilter
from tests.helpers.utils import path
from tests.mocks.common import ANY_DICT, ERROR_RESPONSES

# Targets paths

SEND = path(Session.send)
REQUEST = path(HTTPRetryHelper.request)

IS_SET = path(Event.is_set)
READ_CSV = f"{TemplateContextBuilder.__module__}.read_csv"

SEARCH_ARTICLES = path(ScopusSearchAPI.search_articles)
GET_ARTICLES_PAGE = path(ScopusArticlesPage.get_articles_page)

SET_SUBSET = path(ArticlesPageScraper.set_subset)
SCRAPE = path(ArticlesPageScraper.scrape)
FILTER = path(ArticlesSimilarityFilter.filter)
GET_ARTICLES = path(ScopusArticlesAggregator.get_articles)


# Class Instances

HANDLER = ExceptionHandler()

ACCESS_TOKEN = AccessToken()
QUERY_PARAMS = QueryParams()

HTTP_HELPER = HTTPRetryHelper()
URL_BUILDER = URLBuilderHelper()

SEARCH_API = ScopusSearchAPI(HTTP_HELPER, URL_BUILDER)
ARTICLES_PAGE = ScopusArticlesPage(HTTP_HELPER, URL_BUILDER)

ARTICLES_AGGREGATOR = ScopusArticlesAggregator(
    SEARCH_API, MockArticlesScraper(), MockSimilarityFilter()
)
PAGE_SCRAPER = ArticlesPageScraper(ARTICLES_PAGE)
SIMILARITY_FILTER = ArticlesSimilarityFilter()

# Exceptions Messages

INVALID_SHORT_VALUE = "String should have at least 32 characters"
INVALID_LONG_VALUE = "String should have at most 32 characters"
INVALID_PATTERN = "String should match pattern '^[a-zA-Z0-9]{32}$'"
MIN_SIZE_LIST = "List should have at least 2 items after validation, not 1"
MAX_SIZE_LIST = "List should have at most 4 items after validation, not 5"
FIELD_REQUIRED = "Field required"

# Exceptions

REQUEST_VALIDATION_ERROR = RequestValidationError([ANY_DICT])
RESPONSE_VALIDATION_ERROR = ResponseValidationError([ANY_DICT])
PYDANTIC_VALIDATION_ERROR = ValidationError.from_exception_data(
    ANY_DICT, [InitErrorDetails(type="missing", input="any")]
)
HTTP_EXCEPTION = HTTPException(400, "any")
APPLICATION_ERROR = ApplicationError(500, "any")
SCOPUS_API_ERROR = ScopusAPIError(ERROR_RESPONSES[500])
COMMON_EXCEPTION = ValueError("any")
FASTAPI_HTTP_EXCEPTION = FastAPIHTTPException(500, "any")
STARLETTE_HTTP_EXCEPTION = StarletteHTTPException(500, "any")
