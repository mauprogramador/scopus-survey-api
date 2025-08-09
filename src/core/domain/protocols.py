from typing import Protocol

from pandas import DataFrame

from src.core.common.types import (
    CombinationBundle,
    CombinationParams,
    Json,
    Keyword,
    ResponseBundle,
    SearchParams,
)
from src.core.data.serializers import ScopusEntry, ScopusSearch


class SurveyDetail(Protocol):
    def set_max_count(self, max_count: int) -> None:
        pass

    def set_search_data(self, scopus_search: ScopusSearch) -> None:
        pass

    def set_quota_data(self, response: ResponseBundle) -> None:
        pass

    def set_loss(self, loss: float) -> None:
        pass

    @property
    def log_data(self) -> tuple[Json, int]:
        pass

    @property
    def headers(self) -> dict[str, str]:
        pass


class HTTPClient(Protocol):
    async def request(self, url: str) -> ResponseBundle:
        pass

    async def close(self) -> None:
        pass


class URLBuilder(Protocol):
    @staticmethod
    def article_page_url(scopus_id: str) -> str:
        pass

    def set_combination_query(self, params: CombinationParams) -> None:
        pass

    def combination_url(
        self, arrangement: tuple[Keyword, ...]
    ) -> CombinationBundle:
        pass

    def search_url(self, params: SearchParams) -> str:
        pass

    def pagination_url(self, page: int) -> str:
        pass

    def set_abstract_query(self, api_key: str) -> None:
        pass

    def abstract_url(self, abstract_url: str) -> str:
        pass


class SearchAPI(Protocol):

    async def survey_totals_found(
        self, bundles_map: dict[int, CombinationBundle]
    ) -> list[Json]:
        pass

    async def search_articles(self, params: SearchParams) -> list[ScopusEntry]:
        pass


class AbstractAPI(Protocol):
    async def retrieve_abstracts(
        self, api_key: str, entry: list[ScopusEntry]
    ) -> DataFrame:
        pass


class SimilarityFilter(Protocol):
    def filter(self, dataframe: DataFrame, similarity_ratio: int) -> DataFrame:
        pass
