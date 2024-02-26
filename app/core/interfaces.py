from abc import ABCMeta, abstractmethod
from typing import TypeAlias

from fastapi.responses import FileResponse
from requests import Response


class ApiParams(metaclass=ABCMeta):
    KeywordsType: TypeAlias = list[str]

    api_key: str
    keywords: KeywordsType


class UseCase(metaclass=ABCMeta):
    ParamsType: TypeAlias = ApiParams

    @classmethod
    @abstractmethod
    def search_articles(cls, data: ParamsType) -> FileResponse:
        pass


class GatewaySearch(metaclass=ABCMeta):
    ParamsType: TypeAlias = ApiParams
    SearchType: TypeAlias = list[dict[str, str]]

    @staticmethod
    @abstractmethod
    def search_articles(data: ParamsType) -> SearchType:
        pass


class GatewayScraping(metaclass=ABCMeta):
    ScrapType: TypeAlias = tuple[str, str]

    @staticmethod
    @abstractmethod
    def scraping_article(scopus_id: str) -> ScrapType:
        pass


class Helper(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def make_request(url: str, headers: dict) -> Response:
        pass
