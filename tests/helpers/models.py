from json import dumps, loads

from fastapi.datastructures import URL
from pandas import DataFrame
from starlette.datastructures import QueryParams

from app.core.config.config import (
    API_KEY_HEADER,
    KEYWORDS_HEADER,
    TOKEN_HEADER,
)
from app.core.config.scopus import QUOTA_EXCEEDED, RATE_LIMIT_EXCEEDED
from app.core.domain.metaclasses import SimilarityFilter


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
        self.headers = headers if headers else {TOKEN_HEADER: token}
        self.query: dict[str, str] = {}
        self.client = None
        if api_key:
            self.query.update({API_KEY_HEADER: api_key})
        if keywords:
            self.query.update({KEYWORDS_HEADER: keywords})

    @property
    def query_params(self):
        return QueryParams(self.query)

    @property
    def method(self):
        return "GET"

    @property
    def url(self):
        return URL("http://any.com")


class Response:
    """Fake Response"""

    def __init__(self, content: dict | str = None, code: int = None) -> None:
        """Fake Response"""
        if content or isinstance(content, str) and len(content) == 0:
            self.text = content if isinstance(content, str) else dumps(content)
        self.status_code = code or 200
        self.body = "any".encode()

    def json(self) -> dict:
        return loads(self.text)


class HeadersResponse:
    """Fake Quota and Rate Limit Exceeded Response"""

    def __init__(self, for_rate: bool = None) -> None:
        """Fake Quota and Rate Limit Exceeded Response"""
        self.status_code = 429
        self.__for_rate = for_rate
        self.headers = {"X-RateLimit-Reset": "1724320891"}
        if not self.__for_rate:
            self.headers.update({"X-ELS-Status": QUOTA_EXCEEDED})

    def json(self) -> dict:
        if self.__for_rate:
            return {"error-response": {"error-code": RATE_LIMIT_EXCEEDED}}
        return {"any": "any"}


class MockSimilarityFilter(SimilarityFilter):

    def filter(self, dataframe: DataFrame) -> DataFrame:
        return dataframe
