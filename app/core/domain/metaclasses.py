from abc import ABCMeta, abstractmethod

from fastapi.responses import FileResponse
from pandas import DataFrame
from requests import Response

from app.core.common.types import Context, Headers, Keywords, SearchParams
from app.core.data.dtos import ScrapeData


class HttpRetry(metaclass=ABCMeta):
    @abstractmethod
    def mount_session(self, headers: Headers) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def request(self, url: str) -> Response:
        pass


class UrlBuilder(metaclass=ABCMeta):
    @abstractmethod
    def get_search_url(self, keywords: Keywords) -> str:
        pass

    @abstractmethod
    def get_pagination_url(self, page: int) -> str:
        pass

    @abstractmethod
    def get_article_page_url(self, scopus_id: str) -> str:
        pass


class SearchAPI(metaclass=ABCMeta):
    @abstractmethod
    def search_articles(self, search_params: SearchParams) -> DataFrame:
        pass


class ArticlesPage(metaclass=ABCMeta):
    @abstractmethod
    def get_articles_page(self, subset: DataFrame) -> DataFrame:
        pass


class ArticlesAggregator(metaclass=ABCMeta):
    @abstractmethod
    def get_articles(self, params: SearchParams) -> FileResponse:
        pass


class ArticlesScraper(metaclass=ABCMeta):
    @abstractmethod
    def set_subset(self, subset: DataFrame) -> None:
        pass

    @abstractmethod
    def scrape(self, index: int) -> ScrapeData:
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
