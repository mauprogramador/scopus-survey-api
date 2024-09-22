from abc import ABCMeta, abstractmethod

from fastapi.responses import FileResponse
from pandas import DataFrame
from requests import Response

from app.core.common.types import Context, Headers, Keywords
from app.core.data.dtos import SearchParams
from app.core.data.serializers import ScopusResult


class HTTPRetry(metaclass=ABCMeta):
    @abstractmethod
    def mount_session(self, headers: Headers) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def request(self, url: str) -> Response:
        pass


class URLBuilder(metaclass=ABCMeta):
    @abstractmethod
    def get_search_url(self, keywords: Keywords) -> str:
        pass

    @abstractmethod
    def get_pagination_url(self, page: int) -> str:
        pass

    @abstractmethod
    def get_abstract_url(self, url: str) -> str:
        pass


class SearchAPI(metaclass=ABCMeta):
    @abstractmethod
    def search_articles(
        self, search_params: SearchParams
    ) -> list[ScopusResult]:
        pass


class AbstractAPI(metaclass=ABCMeta):
    @abstractmethod
    def retrieve_abstracts(
        self, api_key: str, entry: list[ScopusResult]
    ) -> DataFrame:
        pass


class ArticlesAggregator(metaclass=ABCMeta):
    @abstractmethod
    def get_articles(self, params: SearchParams) -> FileResponse:
        pass


class SimilarityFilter(metaclass=ABCMeta):
    @abstractmethod
    def filter(self, dataframe: DataFrame) -> DataFrame:
        pass


class TemplateContext(metaclass=ABCMeta):
    @abstractmethod
    def get_web_app_context(self) -> Context:
        pass

    @abstractmethod
    def get_table_context(self) -> Context:
        pass
