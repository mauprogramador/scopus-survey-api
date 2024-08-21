from json import dumps, loads

from fastapi.datastructures import URL
from pandas import DataFrame
from starlette.datastructures import QueryParams

from app.core.config.config import (
    API_KEY_HEADER,
    KEYWORDS_HEADER,
    TOKEN_HEADER,
)
from app.core.data.dtos import ScrapeData
from app.core.domain.metaclasses import ArticlesScraper, SimilarityFilter


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
    """Fake Quota Exceeded Response"""

    __STATUS = "QUOTA_EXCEEDED - Quota Exceeded"

    def __init__(
        self, code: int = None, status: str = None, reset: int = None
    ) -> None:
        """Fake Quota Exceeded Response"""
        self.status_code = code if code else 429
        self.headers = {
            "X-ELS-Status": status if status else self.__STATUS,
            "X-RateLimit-Reset": reset if reset else 1724320891,
        }

    def json(self) -> dict:
        return {"any": "any"}


class MockArticlesScraper(ArticlesScraper):

    def set_subset(self, subset: DataFrame) -> None:
        pass

    def scrape(self, index: int) -> ScrapeData:
        return ScrapeData(index, "any", "any", "any")


class MockSimilarityFilter(SimilarityFilter):

    def filter(self, dataframe: DataFrame) -> DataFrame:
        return dataframe
