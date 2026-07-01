import asyncio
import io
import random
from http import HTTPMethod, HTTPStatus
from types import FunctionType
from typing import Any, Callable, Literal, Self, Type, TypeAlias
from unittest.mock import AsyncMock, MagicMock, Mock

import aiohttp
import aiohttp_retry as aioretry
import httpx
import pandas as pd
from fastapi.responses import FileResponse, JSONResponse
from pandas import DataFrame

from src.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from src.adapters.gateway.scopus_search_api import ScopusSearchAPI
from src.adapters.helpers.http_client import HTTPClient
from src.adapters.helpers.url_builder import URLBuilder
from src.core.common.types import CombinationBundle, Json, ResponseBundle
from src.core.config.config import DIRECTORY
from src.core.config.scopus import MAX_ITEMS_PER_PAGE
from src.core.data.serializers import ScopusPage
from src.core.data.survey_details import SurveyDetails
from src.core.data.survey_state import SurveyState
from src.core.domain.translations import translate_error
from src.core.use_cases.similarity_filter import SimilarityFilter
from src.core.use_cases.survey_orchestrator import SurveyOrchestrator
from tests.mocks.raw import (
    CSV_FILE_NAME,
    HTTP_200,
    LOG_QUOTA,
    RAW_ENTRY,
    RAW_HEADERS_OK,
    REQUEST,
    RESET,
    SCOPUS_ID,
    SKIPROWS,
)


Target: TypeAlias = Type | FunctionType | Callable


def fqn(target: Target, method: Target = None, altname: str = None) -> str:
    """Gets the Fully Qualified Name for mocker.patch target"""
    if method is None:
        return f"{target.__module__}.{target.__qualname__}"

    if altname is not None:
        return f"{target.__module__}.{altname}.{method.__name__}"

    return f"{target.__module__}.{method.__name__}"


def spec(target: Target, method: Target = None, altname: str = None) -> Json:
    """Gets F.Q.N. for mocker.patch target and spec"""
    if method is None:
        return {"target": fqn(target), "spec": target}
    return {"target": fqn(target, method, altname), "spec": method}


def trans(exc: Exception) -> str:
    return translate_error(REQUEST, exc)


def mock_combination_url(*_) -> CombinationBundle:
    """Mock URLBuilder.combination_url"""
    return CombinationBundle(combination="any", url="any")


async def mock_survey_totals_found(
    bundles_map: dict[int, CombinationBundle],
) -> list[Json]:
    """Mock ScopusSearchAPI.survey_totals_found"""
    for index in bundles_map.keys():
        bundles_map[index].total = random.randint(16, 256)
    return [bundle.model_dump() for bundle in bundles_map.values()]


def mock_filter(dataframe: DataFrame, *_) -> DataFrame:
    """Mock SimilarityFilter.filter"""
    return dataframe


async def mock_survey_combinations(*_) -> JSONResponse:
    """Mock KeywordsScouter.survey_combinations"""
    return JSONResponse({"Any": "any"})


async def mock_retrieve_articles(*_) -> FileResponse:
    """Mock SurveyOrchestrator.retrieve_articles"""
    return FileResponse(DIRECTORY / CSV_FILE_NAME)


def mock_from_iterable(*_) -> tuple[str, ...]:
    """Mock itertools.chain.from_iterable"""
    return ("Python",)


def load_csv_from_response(res: httpx.Response) -> DataFrame:
    """Load DataFrame from CSV file response ignoring metadata"""
    buffer_data = io.StringIO(res.content.decode())
    return pd.read_csv(
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
) -> Json:
    """Build a raw abstract response"""
    return {
        "abstracts-retrieval-response": {
            "coredata": {
                "dc:identifier": SCOPUS_ID,
                "dc:title": title if title else "any_title",
                "prism:doi": f"10.{random.randint(1111, 9999)}0/any",
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
        spec=aiohttp.ClientResponse,
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


def get_patch(value: Any | list[Any] | Exception) -> tuple[str, AsyncMock]:
    """Patch AIOHTTP Retry.get"""
    if isinstance(value, (list, BaseException)):
        new = AsyncMock(aiohttp.ClientResponse, side_effect=value)
    else:
        new = AsyncMock(aiohttp.ClientResponse, return_value=value)
    return fqn(aioretry.RetryClient.get), new


class Patch:
    """Context for mocker.patch params
    Args:
        method: Type | FunctionType | Callable
        altname: str
        value: Exception | Any
    """

    _VALUE_KEYS = ("side_effect", "return_value")

    def __init__(self, target: Target, *args: Any) -> None:
        """Context for mocker.patch params
        Args:
            method: Type | FunctionType | Callable
            altname: str
            value: Exception | Any
        """

        self._keys = ["target", "spec"]
        self.target: str = None
        self.spec: Target = None
        self.side_effect: Any = None
        self.return_value: Any = None

        method: Target | None = None
        value: Exception | Any = None
        altname: str | None = None

        for arg in args:
            if isinstance(arg, Target):
                method = arg
            elif isinstance(arg, str):
                altname = arg
            else:
                value = arg

        self.target = fqn(target, method, altname)
        self.spec = target if method is None else method
        self._handle_value(value)

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
        state: SurveyState,
        api: ScopusSearchAPI | ScopusAbstractRetrievalAPI,
    ) -> None:
        """Context for ScopusAPIs and its dependencies"""
        self.req = request
        self.details = details
        self.state = state
        self.api = api


class AggFix:
    """Context for SurveyOrchestrator and its dependencies"""

    def __init__(
        self,
        use_case: SurveyOrchestrator,
        similarity_filter: Mock,
        set_loss: Mock,
    ) -> None:
        """Context for SurveyOrchestrator and its dependencies"""
        self.use_case = use_case
        self.filter = similarity_filter
        self.set_loss = set_loss


class MockState(SurveyState):
    """Mock SurveyState"""

    def __init__(
        self, responses_count: int = None, total_results: int = None
    ) -> None:
        """Mock SurveyState"""
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


class MockAsyncContext:
    """Mock async contexts `async with`"""

    def __call__(self, *args: Any, **kwds: Any) -> Self:
        return self

    async def __await__(self):
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockSemaphore(asyncio.Semaphore):
    def __init__(self, value: int = 1) -> None:
        super().__init__(value)
        self.acquires: list[Json] = []
        self.releases: list[Json] = []

    def __call__(self) -> Any:
        return self

    async def acquire(self) -> Literal[True]:
        self.acquires.append(
            # pylint: disable=W0212
            {"value": self._value, "waiters": len(self._waiters or [])}
        )
        return await super().acquire()

    def release(self) -> None:
        self.releases.append(
            # pylint: disable=W0212
            {"value": self._value, "waiters": len(self._waiters or [])}
        )
        return super().release()


def search_fix(value: Any | Exception) -> APIsFix:
    """Fixture for ScopusSearchAPI and its dependencies"""
    if isinstance(value, (list, BaseException)):
        api_call_mock = AsyncMock(HTTPClient.api_call, side_effect=value)
    else:
        api_call_mock = AsyncMock(HTTPClient.api_call, return_value=value)

    details = SurveyDetails()
    state = MockState()
    api = ScopusSearchAPI(
        AsyncMock(HTTPClient, api_call=api_call_mock),
        MagicMock(URLBuilder),
        details,
        state,
    )
    return APIsFix(api_call_mock, details, state, api)


def abstract_fix(
    value: Any | Exception, first_search: Json, responses_count: int = None
) -> APIsFix:
    """Fixture for ScopusAbstractAPI and its dependencies"""
    search_results = ScopusPage(**first_search)

    details = SurveyDetails()
    details.set_search_data(search_results)

    if isinstance(value, (list, BaseException)):
        api_call_mock = AsyncMock(HTTPClient.api_call, side_effect=value)
    else:
        api_call_mock = AsyncMock(HTTPClient.api_call, return_value=value)

    if responses_count is None:
        state = MockState()
    else:
        state = MockState(responses_count, search_results.total_results)

    state.set_first_search(search_results)

    api = ScopusAbstractRetrievalAPI(
        AsyncMock(HTTPClient, api_call=api_call_mock),
        MagicMock(URLBuilder),
        details,
        state,
    )
    return APIsFix(api_call_mock, details, state, api)


def aggregator_fix(value: DataFrame) -> AggFix:
    """Fixture for SurveyOrchestrator and its dependencies"""
    retrieve = AsyncMock(
        ScopusAbstractRetrievalAPI.retrieve_abstracts, return_value=value
    )
    similarity_filter = Mock(SimilarityFilter.filter, side_effect=mock_filter)
    set_loss = Mock(SurveyDetails().set_loss)
    use_case = SurveyOrchestrator(
        AsyncMock(ScopusSearchAPI, http_client=AsyncMock(HTTPClient)),
        AsyncMock(
            ScopusAbstractRetrievalAPI,
            retrieve_abstracts=retrieve,
        ),
        MagicMock(SimilarityFilter, filter=similarity_filter),
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
