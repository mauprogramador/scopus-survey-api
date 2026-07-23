from collections.abc import Callable
from gettext import GNUTranslations
from typing import (
    Annotated,
    Any,
    Literal,
    NamedTuple,
    Protocol,
    TypedDict,
)

from pandas import DataFrame
from pydantic import Field

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


type Keyword = Annotated[
    str, Field(pattern=_KEYWORD_PATTERN, min_length=2, max_length=120)
]

type Json = dict[str, Any]

type Translations = dict[Lang, GNUTranslations]

type Token = Annotated[
    str, Field(pattern=_TOKEN_PATTERN, min_length=64, max_length=64)
]

type URLBuilder = Callable[[str | int], str]

type Headers = dict[str, str]

type APIName = Literal["search", "abstract"]


class ScopusEntry(Protocol):
    url: str
    scopus_id: str


class ScopusPage(Protocol):
    total_results: int
    items_per_page: int
    entry: list[ScopusEntry]

    def details(self) -> dict[str, Any]:
        pass


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
    page_range: PageRange
    keywords: list[str]

    def model_dump(self, **kwargs) -> dict[str, Any]:
        pass

    @property
    def date(self) -> str:
        pass


class SurveyParams(CombinationParams):
    combination: str
    ratio: int


class ScopusHeaders(Protocol):
    limit: int | None
    remaining: int | None
    reset: int | None
    status: str | None

    @property
    def reset_datetime(self) -> str | None:
        pass


class TotalBundle(TypedDict):
    index: int
    combination: str
    total: int


class ResponseBundle(NamedTuple):
    code: int
    headers: dict[str, str]
    data: dict[str, Any]


class ScopusDetails(NamedTuple):
    search_result: ScopusPage
    pages_count: int
    total_retrieved: int
    search_headers: ScopusHeaders
    abstract_headers: ScopusHeaders


class SurveyDetails(NamedTuple):
    search_result: ScopusPage
    pages_count: int
    total_retrieved: int
    search_headers: ScopusHeaders
    abstract_headers: ScopusHeaders
    total_final: int


class HTTPClient(Protocol):

    async def api_call(self, url: str) -> ResponseBundle:
        pass

    async def close(self) -> None:
        pass


class VolumeScouter(Protocol):

    async def fetch(
        self, params: CombinationParams, combinations: list[str]
    ) -> tuple[list[Json], ScopusHeaders]:
        pass


class DatasetGatherer(Protocol):

    async def fetch(
        self, params: SurveyParams
    ) -> tuple[list[Json], ScopusDetails]:
        pass


class SimilarityFilter(Protocol):

    def filter(self, dataframe: DataFrame, similarity_ratio: int) -> DataFrame:
        pass
