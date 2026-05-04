from typing import Annotated, Any, NamedTuple, Protocol, TypeAlias, TypeVar

from pydantic import BaseModel, Field, TypeAdapter

from src.core.common.patterns import KEYWORD_PATTERN, TOKEN_PATTERN
from src.core.data.enums import DocType, PageRange, PubStage, SrcType, SubjArea


Keyword: TypeAlias = Annotated[
    str, Field(pattern=KEYWORD_PATTERN, min_length=2, max_length=70)
]

Json: TypeAlias = dict[str, Any]

Articles: TypeAlias = list[dict[str, str]]

ScopusModel = TypeVar("ScopusModel", bound=BaseModel)

Token: TypeAdapter[str | None] = TypeAdapter(
    Annotated[
        str | None,
        Field(
            pattern=TOKEN_PATTERN,
            min_length=40,
            max_length=40,
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
