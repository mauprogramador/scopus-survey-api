from abc import ABCMeta, abstractmethod

from aiohttp import ClientResponse
from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse
from pandas import DataFrame
from pydantic import BaseModel

from src.adapters.presenters.error_response import ErrorJSON
from src.core.common.types import SearchParams
from src.core.data.enums import Lang
from src.core.data.serializers import ScopusEntry


class HTTPClientABC(metaclass=ABCMeta):
    @abstractmethod
    async def request(self, url: str) -> ClientResponse:
        pass

    @abstractmethod
    async def close(self) -> None:
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
    def abstract_url(self, abstract_url: str) -> str:
        pass


class SearchAPIABC(metaclass=ABCMeta):
    @abstractmethod
    async def search_articles(self, params: SearchParams) -> list[ScopusEntry]:
        pass


class AbstractAPIABC(metaclass=ABCMeta):
    @abstractmethod
    def retrieve_abstracts(
        self, api_key: str, entry: list[ScopusEntry]
    ) -> DataFrame:
        pass


class ScopusResponseABC(metaclass=ABCMeta):
    @abstractmethod
    def validate(self, response: ClientResponse) -> BaseModel:
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
    def search_template(
        cls, request: Request, csrf_token: str, lang: Lang
    ) -> HTMLResponse:
        pass

    @classmethod
    @abstractmethod
    def not_found_template(
        cls, request: Request, response: ErrorJSON
    ) -> HTMLResponse:
        pass


class CSVResponseABC(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def build(
        cls,
        api_key: str,
        headers: dict[str, str] | None = None,
    ) -> FileResponse:
        pass
