from threading import Event
from unittest.mock import Mock

from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic_core import InitErrorDetails, PydanticUndefined, ValidationError
from requests.sessions import Session
from slowapi.errors import Limit, RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from src.adapters.gateway.scopus_search_api import ScopusSearchAPI
from src.adapters.helpers.http_retry import HTTPRetry
from src.adapters.helpers.scopus_response import ScopusResponse
from src.adapters.helpers.url_builder import URLBuilder
from src.adapters.presenters.html_response import TemplateBuilder
from src.core.common.messages import ABSTRACT_API_ERROR as ABSTRACT_ERROR_MSG
from src.core.common.messages import SEARCH_API_ERROR as SEARCH_ERROR_MSG
from src.core.data.query_params import CSVParams, SearchParams
from src.core.data.serializers import ScopusAbstract, ScopusSearch
from src.core.data.survey_detail import SurveyDetail
from src.core.domain.http_exceptions import HTTPError, ScopusAPIError
from src.core.use_cases import (
    ArticlesSimilarityFilter,
    ScopusArticlesAggregator,
)
from src.framework.middleware.exception_handler import ExceptionHandler
from tests.helpers.models import MockSimilarityFilter
from tests.helpers.utils import path
from tests.mocks.common import API_KEY, CSRF_TOKEN, KEYWORDS

# Targets paths

SEND = path(Session.send)
REQUEST = path(HTTPRetry.request)

IS_SET = path(Event.is_set)
READ_CSV = f"{TemplateBuilder.__module__}.read_csv"

HANDLE = path(ScopusResponse.validate)

SEARCH_ARTICLES = path(ScopusSearchAPI.search_articles)
RETRIEVE_ABSTRACT = path(ScopusAbstractRetrievalAPI.retrieve_abstracts)

FILTER = path(ArticlesSimilarityFilter.filter)
GET_ARTICLES = path(ScopusArticlesAggregator.retrieve_articles)


# Class Instances

HANDLER = ExceptionHandler()

ACCESS_TOKEN = CSVParams(**{"csrf_token": CSRF_TOKEN, "api_key": API_KEY})
QUERY_PARAMS = SearchParams(
    **{"csrf_token": CSRF_TOKEN, "api_key": API_KEY, "keywords": KEYWORDS}
)

URL_BUILDER = URLBuilder()
HTTP_RETRY = HTTPRetry(for_search=True)
SURVEY_DETAIL = SurveyDetail()

SEARCH_RESPONSE = ScopusResponse(ScopusSearch, SEARCH_ERROR_MSG)
ABSTRACT_RESPONSE = ScopusResponse(ScopusAbstract, ABSTRACT_ERROR_MSG)

SEARCH_API = ScopusSearchAPI(
    HTTP_RETRY, URL_BUILDER, SEARCH_RESPONSE, SURVEY_DETAIL
)

ABSTRACT_API = ScopusAbstractRetrievalAPI(
    HTTP_RETRY, URL_BUILDER, ABSTRACT_RESPONSE, SURVEY_DETAIL
)

ARTICLES_AGGREGATOR = ScopusArticlesAggregator(
    SEARCH_API, ABSTRACT_API, MockSimilarityFilter(), SURVEY_DETAIL
)

SIMILARITY_FILTER = ArticlesSimilarityFilter()


# Exceptions

HTTP_ERROR = HTTPError(400, "any")
SCOPUS_API_ERROR = ScopusAPIError(500, {"any": "any"}, "any")

STARLETTE_HTTP_EXCEPTION = StarletteHTTPException(500, "any")
FASTAPI_HTTP_EXCEPTION = FastAPIHTTPException(500, "any")

REQUEST_VALIDATION_ERROR = RequestValidationError([{"msg": "any"}])
RESPONSE_VALIDATION_ERROR = ResponseValidationError([{"msg": "any"}])

RESPONSE_VALIDATION_EXCEPTION_ERROR = ResponseValidationError(
    [{"msg": "any", "ctx": {"error": ValueError("any")}}]
)

PYDANTIC_VALIDATION_ERROR = ValidationError.from_exception_data(
    "any", [InitErrorDetails(type="missing", input="any")]
)

PYDANTIC_UNDEFINED_ERROR = ValidationError.from_exception_data(
    "any", [InitErrorDetails(type="missing", input=PydanticUndefined)]
)

RATE_LIMIT_ERROR = RateLimitExceeded(Mock(Limit, error_message="any"))
