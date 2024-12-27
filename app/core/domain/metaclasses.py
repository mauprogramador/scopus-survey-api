from abc import ABCMeta, abstractmethod

from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse
from pandas import DataFrame
from requests import Response as RResponse
from starlette.responses import Response as SResponse

from app.core.data.enums import Language
from app.core.data.validators import SearchParams
from app.core.data.serializers import ScopusResult


class HTTPHelper(metaclass=ABCMeta):
    @abstractmethod
    def mount_session(self, headers: dict[str, str]) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def request(self, url: str) -> RResponse:
        pass


class URLHelper(metaclass=ABCMeta):
    @abstractmethod
    def get_search_url(self, keywords: list[str]) -> str:
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


class TemplateHelper(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def search_template(cls, request: Request, lang: Language) -> HTMLResponse:
        pass

    @classmethod
    @abstractmethod
    def table_template(
        cls, request: Request, lang: Language, api_key: str
    ) -> HTMLResponse:
        pass

    @classmethod
    @abstractmethod
    def not_found_template(
        cls,
        request: Request,
        response: SResponse,
        message: str,
    ) -> HTMLResponse:
        pass


class CSVResponseABC(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def build(cls, api_key: str, dataframe: DataFrame = None) -> FileResponse:
        pass
