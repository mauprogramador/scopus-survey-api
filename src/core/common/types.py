from gettext import GNUTranslations
from typing import Annotated, Any, NamedTuple, Protocol, TypeAlias, TypeVar

from pydantic import BaseModel, Field, TypeAdapter

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

Token: TypeAdapter[str | None] = TypeAdapter(
    Annotated[
        str | None,
        Field(
            pattern=_TOKEN_PATTERN,
            min_length=64,
            max_length=64,
        ),
    ]
)


class LogParams(NamedTuple):
    host: str
    port: int
    logging_file: bool
    debug: bool


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
