from http import HTTPMethod, HTTPStatus
from io import StringIO
from random import randint
from types import FunctionType, MethodType
from typing import Any, Callable, Self, Type, TypeAlias
from unittest.mock import AsyncMock, MagicMock, Mock

from aiohttp import ClientResponse
from aiohttp_retry import RetryClient
from fastapi.responses import FileResponse, JSONResponse
from httpx import Response
from pandas import DataFrame, read_csv

from src.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from src.adapters.gateway.scopus_search_api import ScopusSearchAPI
from src.adapters.helpers.http_client import HTTPClient
from src.adapters.helpers.url_builder import URLBuilder
from src.core.common.types import CombinationBundle, Json, ResponseBundle
from src.core.config.config import DIRECTORY
from src.core.config.scopus import MAX_ITEMS_PER_PAGE
from src.core.data.quota_results_handler import QuotaResultsHandler
from src.core.data.serializers import ScopusSearch
from src.core.data.survey_details import SurveyDetails
from src.core.use_cases.articles_similarity_filter import (
    ArticlesSimilarityFilter,
)
from src.core.use_cases.scopus_articles_aggregator import (
    ScopusArticlesAggregator,
)
from tests.mocks.raw import (
    CSV_FILE_NAME,
    HTTP_200,
    LOG_QUOTA,
    RAW_ENTRY,
    RAW_HEADERS_OK,
    RESET,
    SCOPUS_ID,
    SKIPROWS,
)


Target: TypeAlias = Type | MethodType | FunctionType | Callable


def fqn(target: Target, method: Target = None) -> str:
    """Gets the Fully Qualified Name"""
    if method is None:
        return f"{target.__module__}.{target.__qualname__}"

    if isinstance(method, MethodType):
        class_name = method.__self__.__class__.__name__
        method_name = method.__name__
        return f"{target.__module__}.{class_name}.{method_name}"

    if isinstance(method, (Type, FunctionType, Callable)):
        return f"{target.__module__}.{method.__name__}"

    if hasattr(method, "__name__"):
        return f"{target.__module__}.{method.__name__}"

    return f"{target.__module__}.{method.__class__.__name__}"


def mock_combination_url(*_) -> CombinationBundle:
    """Mock URLBuilder.combination_url"""
    return CombinationBundle(combination="any", url="any")


async def mock_survey_totals_found(
    bundles_map: dict[int, CombinationBundle],
) -> list[Json]:
    """Mock ScopusSearchAPI.survey_totals_found"""
    for index in bundles_map.keys():
        bundles_map[index].total = randint(16, 256)
    return [bundle.model_dump() for bundle in bundles_map.values()]


def mock_filter(dataframe: DataFrame, *_) -> DataFrame:
    """Mock ArticlesSimilarityFilter.filter"""
    return dataframe


async def mock_survey_combinations(*_) -> JSONResponse:
    """Mock KeywordCombinationFinder.survey_combinations"""
    return JSONResponse({"Any": "any"})


async def mock_retrieve_articles(*_) -> FileResponse:
    """Mock ScopusArticlesAggregator.retrieve_articles"""
    return FileResponse(DIRECTORY / CSV_FILE_NAME)


def mock_from_iterable(*_) -> tuple[str, ...]:
    """Mock itertools.chain.from_iterable"""
    return ("Python",)


def load_csv_from_response(response: Response) -> DataFrame:
    """Load DataFrame from CSV file response ignoring metadata"""
    buffer_data = StringIO(response.content.decode())
    return read_csv(
        buffer_data, sep=";", skiprows=SKIPROWS, keep_default_na=False
    )


def search_raw(total_results: int, entry_count: int | None = None) -> Json:
    """Build a raw search response"""
    items_per_page = min(total_results, MAX_ITEMS_PER_PAGE)
    count = items_per_page if entry_count is None else entry_count
    return {
        "search-results": {
            "opensearch:totalResults": str(total_results),
            "opensearch:itemsPerPage": str(items_per_page),
            "entry": [RAW_ENTRY] * count,
        }
    }


def abstract_raw(
    title: str | None = None,
    author: str | None = None,
    date: str | None = None,
) -> dict[str, Any]:
    """Build a raw abstract response"""
    return {
        "abstracts-retrieval-response": {
            "coredata": {
                "dc:identifier": SCOPUS_ID,
                "dc:title": title if title else "any_title",
                "prism:doi": f"10.{randint(1111, 9999)}0/any",
                "prism:coverDate": date if date else "any_date",
                "dc:creator": {
                    "author": [
                        {"ce:indexed-name": author if author else "any_author"}
                    ]
                },
            }
        }
    }


def headers_raw(remaining: int) -> dict[str, str]:
    """Build a raw response headers"""
    return {
        "X-RateLimit-Limit": "20000",
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(RESET),
        "X-ELS-Status": "OK",
    }


def response_mock(
    value: Json | None | Exception,
    status: HTTPStatus | None = None,
    headers: dict[str, str] | None = None,
) -> MagicMock:
    """Mock AIOHTTP ClientResponse"""
    if isinstance(value, dict) or value is None:
        json = AsyncMock(type(value).__qualname__, return_value=value)
    else:
        json = AsyncMock(type(value).__qualname__, side_effect=value)
    return MagicMock(
        spec=ClientResponse,
        status=status if status else HTTP_200,
        method=HTTPMethod.GET,
        headers=headers if headers else RAW_HEADERS_OK,
        json=json,
        text=AsyncMock(return_value=str(value)),
    )


def bundle_mock(
    value: Json,
    status: HTTPStatus | None = None,
    headers: dict[str, str] | None = None,
) -> ResponseBundle:
    """Mock ResponseBundle"""
    return ResponseBundle(
        code=status if status else HTTP_200,
        headers=headers if headers else RAW_HEADERS_OK,
        data=value,
    )


def get_patch(value: Any | Exception) -> tuple[str, AsyncMock]:
    """Patch AIOHTTP Retry.get"""
    if isinstance(value, (list, BaseException)):
        new = AsyncMock(ClientResponse, side_effect=value)
    else:
        new = AsyncMock(ClientResponse, return_value=value)
    return fqn(RetryClient.get), new


def http_patch(target: Target) -> tuple[str, AsyncMock]:
    """Patch AsyncLimiter and Semaphore With Context"""
    if target.__name__ == "__aexit__":
        return fqn(target), AsyncMock(target, return_value=False)
    return fqn(target), AsyncMock(target)


class Patch:
    """Context for mocker.patch params
    Args:
        method: Type | MethodType | FunctionType | Callable
        value: Exception | Any
    """

    _VALUE_KEYS = ("side_effect", "return_value")

    def __init__(self, target: Target, *args: Any) -> None:
        """Context for mocker.patch params
        Args:
            method: Type | MethodType | FunctionType | Callable
            value: Exception | Any
        """
        self._keys = ["target", "spec"]
        self.target: str = None
        self.spec: Target = None
        self.side_effect: Any = None
        self.return_value: Any = None

        method: Target = None
        value: Exception | Any = None

        for arg in args:
            if isinstance(arg, Target):
                method = arg
            else:
                value = arg

        if method is None:
            self.target = fqn(target)
            self.spec = target

        else:
            self.target = fqn(target, method)
            self.spec = method

        self._handle_value(value)

    def classmethod(self, target: Target) -> Self:
        class_method = self.target.split(".")[-2:]
        target_path = fqn(target).split(".")[:-1]
        self.target = ".".join([*target_path, *class_method])

        return self

    def _handle_value(self, value: Exception | Any) -> None:
        if value is None:
            return None

        if isinstance(value, (list, BaseException)):
            self.side_effect = value
            self.return_value = None
        else:
            self.return_value = value
            self.side_effect = None

        for key in self._VALUE_KEYS:
            key_attr_value = getattr(self, key)

            if key_attr_value is not None and key not in self._keys:
                self._keys.append(key)

            elif key_attr_value is None and key in self._keys:
                self._keys.remove(key)

        return None

    def keys(self) -> list[str]:
        return self._keys

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __call__(self, value: Exception | Any) -> Self:
        self._handle_value(value)
        return self


class APIsFix:
    """Context for ScopusAPIs and its dependencies"""

    def __init__(
        self,
        request: AsyncMock,
        details: SurveyDetails,
        state: QuotaResultsHandler,
        api: ScopusSearchAPI | ScopusAbstractRetrievalAPI,
    ) -> None:
        """Context for ScopusAPIs and its dependencies"""
        self.req = request
        self.details = details
        self.state = state
        self.api = api


class AggFix:
    """Context for ScopusArticlesAggregator and its dependencies"""

    def __init__(
        self,
        use_case: ScopusArticlesAggregator,
        similarity_filter: Mock,
        set_loss: Mock,
    ) -> None:
        """Context for ScopusArticlesAggregator and its dependencies"""
        self.use_case = use_case
        self.filter = similarity_filter
        self.set_loss = set_loss


class MockState(QuotaResultsHandler):
    """Mock QuotaResultsHandler"""

    def __init__(
        self, responses_count: int = None, total_results: int = None
    ) -> None:
        """Mock QuotaResultsHandler"""
        super().__init__()
        self._mock_abstracts_to_fetch = responses_count
        self._mock_total_abstracts = total_results

    def __call__(self) -> Self:
        return self

    @property
    def abstracts_to_fetch(self) -> int:
        if self._mock_abstracts_to_fetch is None:
            return self.total_abstracts - self._FIRST_RESULT
        return self._mock_abstracts_to_fetch - self._FIRST_RESULT

    @property
    def abstracts_to_fetch_range(self) -> range:
        if self._mock_abstracts_to_fetch is None:
            return range(self._FIRST_RESULT, self.total_abstracts)
        return range(self._FIRST_RESULT, self._mock_abstracts_to_fetch)

    def validate_integrity(self) -> None:
        pass

    def fix_total(self) -> None:
        if self._mock_total_abstracts is None:
            self.total_abstracts = len(self.entry)
        else:
            self.total_abstracts = self._mock_total_abstracts
        self.abstracts = []


def search_fix(value: Any | Exception) -> APIsFix:
    """Fixture for ScopusSearchAPI and its dependencies"""
    if isinstance(value, (list, BaseException)):
        request = AsyncMock(HTTPClient.request, side_effect=value)
    else:
        request = AsyncMock(HTTPClient.request, return_value=value)

    details = SurveyDetails()
    state = MockState()
    api = ScopusSearchAPI(
        AsyncMock(HTTPClient, request=request),
        MagicMock(URLBuilder),
        details,
        state,
    )
    return APIsFix(request, details, state, api)


def abstract_fix(
    value: Any | Exception, first_search: Json, responses_count: int = None
) -> APIsFix:
    """Fixture for ScopusAbstractAPI and its dependencies"""
    search_results = ScopusSearch(**first_search)

    details = SurveyDetails()
    details.set_search_data(search_results)

    if isinstance(value, (list, BaseException)):
        request = AsyncMock(HTTPClient.request, side_effect=value)
    else:
        request = AsyncMock(HTTPClient.request, return_value=value)

    if responses_count is None:
        state = MockState()
    else:
        state = MockState(responses_count, search_results.total_results)

    state.set_first_search(search_results)

    api = ScopusAbstractRetrievalAPI(
        AsyncMock(HTTPClient, request=request),
        MagicMock(URLBuilder),
        details,
        state,
    )
    return APIsFix(request, details, state, api)


def aggregator_fix(value: DataFrame) -> AggFix:
    """Fixture for ScopusArticlesAggregator and its dependencies"""
    retrieve = AsyncMock(
        ScopusAbstractRetrievalAPI.retrieve_abstracts, return_value=value
    )
    similarity_filter = Mock(
        ArticlesSimilarityFilter.filter, side_effect=mock_filter
    )
    set_loss = Mock(SurveyDetails().set_loss)
    use_case = ScopusArticlesAggregator(
        AsyncMock(ScopusSearchAPI, http_client=AsyncMock(HTTPClient)),
        AsyncMock(
            ScopusAbstractRetrievalAPI,
            retrieve_abstracts=retrieve,
        ),
        MagicMock(ArticlesSimilarityFilter, filter=similarity_filter),
        MagicMock(
            SurveyDetails,
            set_loss=set_loss,
            search_quota=LOG_QUOTA,
            abstract_quota=LOG_QUOTA,
            metadata=["any=any"],
            headers={},
        ),
    )
    return AggFix(use_case, similarity_filter, set_loss)
