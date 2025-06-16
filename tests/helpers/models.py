from http import HTTPStatus
from json import dumps, loads
from typing import Any

from fastapi.datastructures import URL, Headers
from pandas import DataFrame
from starlette.datastructures import QueryParams

from src.core.common.messages import QUOTA_EXCEEDED, RATE_LIMIT_EXCEEDED
from src.core.domain.interfaces import SimilarityFilterABC


class Request:
    """Fake Request"""

    def __init__(
        self,
        token: str | None = None,
        headers: dict | None = None,
        api_key: str | None = None,
        keywords: str | None = None,
    ) -> None:
        """Fake Request"""
        if headers:
            self.headers = Headers(headers)
        else:
            self.headers = Headers({"X-CSRF-Token": f"{token}"})
        self.query: dict[str, str] = {}
        self.client = None
        if api_key:
            self.query.update({"api_key": api_key})
        if keywords:
            self.query.update({"keywords": keywords})

    @property
    def query_params(self):
        return QueryParams(self.query)

    @property
    def method(self):
        return "GET"

    @property
    def url(self):
        return URL("http://any.com/other")

    @property
    def session(self) -> dict[str, Any]:
        return {}

    @property
    def cookies(self) -> dict[str, str]:
        return {}


class Response:
    """Fake Response"""

    def __init__(self, content: dict | str = None, code: int = None) -> None:
        """Fake Response"""
        if content or isinstance(content, str) and len(content) == 0:
            self.text = content if isinstance(content, str) else dumps(content)
        self.status_code = code or HTTPStatus.OK
        self.body = "any".encode()

    def json(self) -> dict:
        return loads(self.text)


class ScopusResponse:

    def __init__(
        self,
        json: dict | None = None,
        headers: dict | None = None,
        code: int | None = None,
    ) -> None:
        if json:
            self.__json = json
        else:
            self.__json = {
                "search-results": {
                    "opensearch:totalResults": 156,
                    "opensearch:itemsPerPage": 25,
                    "entry": [],
                }
            }
        if headers:
            self.headers = headers
        else:
            self.headers = {
                "X-RateLimit-Limit": "20000",
                "X-RateLimit-Remaining": "20000",
                "X-RateLimit-Reset": "1746087344",
                "X-ELS-Status": "OK",
            }
        self.status_code = code if code else HTTPStatus.OK

    @property
    def text(self) -> str | None:
        return "any"

    def json(self) -> dict:
        return self.__json


class HeadersResponse:
    """Fake Quota and Rate Limit Exceeded Response"""

    def __init__(self, for_rate: bool = None) -> None:
        """Fake Quota and Rate Limit Exceeded Response"""
        self.status_code = HTTPStatus.TOO_MANY_REQUESTS
        self.__for_rate = for_rate
        self.headers = {"X-RateLimit-Reset": "1724320891"}
        if not self.__for_rate:
            self.headers.update({"X-ELS-Status": QUOTA_EXCEEDED})

    def json(self) -> dict:
        if self.__for_rate:
            return {"error-response": {"error-code": RATE_LIMIT_EXCEEDED}}
        return {"any": "any"}


class MockSimilarityFilter(SimilarityFilterABC):

    def filter(self, dataframe: DataFrame, similarity_ratio: int) -> DataFrame:
        return dataframe
