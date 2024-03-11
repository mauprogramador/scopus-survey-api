from abc import ABCMeta, abstractmethod
from typing import TypeAlias

from fastapi.responses import FileResponse
from requests import Response, Session


class ApiParams(metaclass=ABCMeta):
    KeywordsType: TypeAlias = list[str]

    api_key: str
    keywords: KeywordsType


class UseCase(metaclass=ABCMeta):
    ParamsType: TypeAlias = ApiParams

    @abstractmethod
    def search_articles(self, data: ParamsType) -> FileResponse:
        pass


class GatewaySearch(metaclass=ABCMeta):
    ParamsType: TypeAlias = ApiParams
    SearchType: TypeAlias = list[dict[str, str]]

    @classmethod
    @abstractmethod
    def search_articles(cls, data: ParamsType) -> SearchType:
        pass


class GatewayScraping(metaclass=ABCMeta):
    ScrapType: TypeAlias = tuple[str, str]

    @staticmethod
    @abstractmethod
    def scraping_article(scopus_id: str) -> ScrapType:
        pass


class Helper(metaclass=ABCMeta):
    @abstractmethod
    def make_request(
        self, url: str, headers: dict, check_status: bool = None
    ) -> Response:
        pass

    @abstractmethod
    def send_request(self, session: Session) -> Response:
        pass


class CSVData(metaclass=ABCMeta):
    TableType: TypeAlias = list[list[str]] | None

    @abstractmethod
    def handle(self) -> TableType:
        pass
