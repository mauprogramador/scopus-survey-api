from typing import Protocol

from pandas import DataFrame

from src.core.common.types import (
    CombinationBundle,
    CombinationParams,
    Json,
    Keyword,
    Quota,
    ResponseBundle,
    SearchParams,
)
from src.core.data.serializers import ScopusEntry, ScopusSearch


class SurveyDetails(Protocol):
    search_quota: tuple[Quota, int]
    abstract_quota: tuple[Quota, int]
    headers: dict[str, str]
    metadata: list[str]

    def set_keywords(self, keywords: list[str]) -> None:
        pass

    def set_combination(self, combination: str) -> None:
        pass

    def set_search_data(self, scopus_search: ScopusSearch) -> None:
        pass

    def set_search_quota(self, response: ResponseBundle) -> None:
        pass

    def set_abstract_quota(self, response: ResponseBundle) -> None:
        pass

    def set_results(self, retrieved: int) -> None:
        pass

    def set_loss(self, loss_amount: int, loss_percent: float) -> None:
        pass

    def set_average_found(self, average: int) -> None:
        pass


class QuotaResultsHandler(Protocol):
    total_results: int
    items_per_page: int
    entry: list[ScopusEntry]
    abstracts: list[Json]
    total_abstracts: int
    pages_count: int

    def handle_search_quota(self, quota: tuple[Quota, int]) -> None:
        pass

    def handle_abstract_quota(self, quota: tuple[Quota, int]) -> None:
        pass


class HTTPClient(Protocol):

    async def update_strategy(self, total_requests: int) -> None:
        pass

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
    http_client: HTTPClient

    async def survey_totals_found(
        self, bundles_map: dict[int, CombinationBundle]
    ) -> list[Json]:
        pass

    async def search_articles(self, params: SearchParams) -> None:
        pass


class AbstractAPI(Protocol):

    async def retrieve_abstracts(self, api_key: str) -> DataFrame:
        pass


class SimilarityFilter(Protocol):

    def filter(self, dataframe: DataFrame, similarity_ratio: int) -> DataFrame:
        pass
