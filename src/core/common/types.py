from gettext import GNUTranslations
from typing import Annotated, Any, NamedTuple, Protocol, TypeAlias, TypeVar

from pandas import DataFrame
from pydantic import BaseModel, Field

from src.core.common.patterns import KEYWORD_PATTERN, TOKEN_PATTERN
from src.core.data.enums import (
    DocType,
    Lang,
    PageRange,
    PubStage,
    SrcType,
    SubjArea,
)


# e.g. Python, "Data Science", COVID-19, H2O2
_KEYWORD_PATTERN = r"^[a-zA-Z0-9\{\}\?\"\*\-\_ ]{2,120}$"

# e.g. 989a5e2a50389ae6a5faf4c271d8bfb30cbbd88c  (Random Hash)
_TOKEN_PATTERN = r"^[a-zA-Z0-9\-\_]{64}$"


Keyword: TypeAlias = Annotated[
    str, Field(pattern=_KEYWORD_PATTERN, min_length=2, max_length=70)
]

Json: TypeAlias = dict[str, Any]

Articles: TypeAlias = list[dict[str, str]]

Trans: TypeAlias = dict[Lang, GNUTranslations]

ScopusModel = TypeVar("ScopusModel", bound=BaseModel)

Token: TypeAlias = Annotated[
    str, Field(pattern=_TOKEN_PATTERN, min_length=64, max_length=64)
]


class Quota(Protocol):
    limit: int
    remaining: int
    reset_datetime: str
    status: str


class CombinationParams(Protocol):
    api_key: str
    start_year: int
    end_year: int
    doctype: DocType
    pubstage: PubStage
    language: str
    open_access: int
    source_type: SrcType
    subject_area: SubjArea
    pages: PageRange
    keywords: list[Keyword]

    def model_dump(self, **kwargs) -> dict[str, Any]:
        pass

    @property
    def date(self) -> str:
        pass


class SearchParams(CombinationParams):
    combination: str
    ratio: int


class ResponseBundle(NamedTuple):
    code: int
    headers: dict[str, str]
    data: Json


class CombinationBundle(BaseModel):
    index: int = Field(default=None)
    combination: str = Field()
    url: str = Field(exclude=True)
    total: int = Field(default=None)


class RateStrategy(NamedTuple):
    rate: float
    backoff: float
    sleep: float
    concurrent: int


class ScopusEntry(Protocol):
    url: str
    scopus_id: str


class ScopusSearch(Protocol):
    total_results: int
    items_per_page: int
    entry: list[ScopusEntry]

    @property
    def pages_count(self) -> int:
        pass


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
    pages_count: int
    total_abstracts: int
    abstracts: list[Json]
    pages_to_fetch: int
    pages_to_fetch_range: range
    pages_to_fetch_progress: tuple[int, int, int]
    abstracts_to_fetch: int
    abstracts_to_fetch_range: range

    def set_first_search(self, first_search: ScopusSearch) -> None:
        pass

    def validate_integrity(self) -> None:
        pass

    def fix_total(self) -> None:
        pass

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
