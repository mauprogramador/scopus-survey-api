from abc import ABCMeta, abstractmethod

from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse
from pandas import DataFrame
from pydantic import BaseModel
from requests import Response as RResponse
from starlette.responses import Response as SResponse

from app.core.data.enums import Language
from app.core.data.query import SearchParams
from app.core.data.serializers import ScopusResult


class HTTPRetryABC(metaclass=ABCMeta):
    @abstractmethod
    def mount_session(self, headers: dict[str, str]) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def request(self, url: str) -> RResponse:
        pass


class URLBuilderABC(metaclass=ABCMeta):
    @abstractmethod
    def search_url(self, params: SearchParams) -> str:
        pass

    @abstractmethod
    def pagination_url(self, page: int) -> str:
        pass

    @abstractmethod
    def set_abstract_api_key(self, api_key: str) -> None:
        pass

    @abstractmethod
    def abstract_url(self, url: str) -> str:
        pass


class SearchAPIABC(metaclass=ABCMeta):
    @abstractmethod
    def search_articles(self, params: SearchParams) -> list[ScopusResult]:
        pass


class AbstractAPIABC(metaclass=ABCMeta):
    @abstractmethod
    def retrieve_abstracts(
        self, api_key: str, entry: list[ScopusResult]
    ) -> DataFrame:
        pass


class ScopusResponseABC(metaclass=ABCMeta):
    @abstractmethod
    def handle(self, response: RResponse) -> BaseModel:
        pass


class ArticlesAggregatorABC(metaclass=ABCMeta):
    @abstractmethod
    def retrieve_articles(self, params: SearchParams) -> FileResponse:
        pass


class SimilarityFilterABC(metaclass=ABCMeta):
    @abstractmethod
    def filter(self, dataframe: DataFrame, similarity_ratio: int) -> DataFrame:
        pass


class TemplateBuilderABC(metaclass=ABCMeta):
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
