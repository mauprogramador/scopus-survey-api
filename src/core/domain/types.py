from enum import StrEnum, unique
from typing import Any, NamedTuple, Protocol

from pandas import DataFrame
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


type Json = dict[str, Any]


@unique
class Lang(StrEnum):
    EN_US = "en-US"
    PT_BR = "pt-BR"

    @property
    def snake_case(self) -> str:
        return self.value.replace("-", "_")

    @property
    def short(self) -> str:
        return self.value.split("-", maxsplit=1)[0]


@unique
class ExcMsg(StrEnum):
    # HTTP client errors
    CONNECTION_ERROR = "Connection error in request"
    CONNECTION_TIMEOUT = "Request connection timeout"
    REQUEST_EXCEPTION = "Unexpected error from request"
    # CSRF Token errors
    INVALID_TOKEN = "Invalid CSRF Token"
    TOKEN_COOKIE_ERROR = "Missing CSRF Token Cookie"
    TOKEN_HEADER_ERROR = "Missing CSRF Token Header"
    TOKEN_SIGNATURE_ERROR = "CSRF Token signatures do not match"
    EXPIRED_TOKEN = "CSRF token has expired"
    # Scopus API errors
    QUOTA_EXCEEDED = "API Key has exceeded the request quota"
    RATE_LIMIT_EXCEEDED = "Request rate limit per second exceeded"
    VALIDATE_ERROR = "Error in validate response from Scopus API"
    INVALID_JSON_ERROR = "Invalid JSON response from Scopus API"
    SCOPUS_API_ERROR = "Scopus API error"
    DATA_MISMATCH_ERROR = "Data sum mismatch in response"
    # Application errors
    INTERNAL_ERROR = "Unexpected internal error occurred"
    SERIALIZE_ERROR = "Error serializing error details"
    ARTICLES_NOT_FOUND = "No articles found"
    CSV_NOT_FOUND = "No CSV file found"
    SLOWAPI_RATE_ERROR = "Request rate limit exceeded"


def mask_secret(secret_value: str) -> str:
    if secret_value.strip() == "":
        return "*" * 12
    return secret_value[:5] + "*" * len(secret_value[5:])


class SecretKey(str):

    def __new__(cls, value: str = None) -> "SecretKey":
        instance = super().__new__(cls, value)
        setattr(instance, "__mask__", mask_secret(value))
        return instance

    def __repr__(self) -> str:
        return getattr(self, "__mask__")

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  #  pylint: disable=w0613
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            function=cls,
            schema=handler(str),
            serialization=core_schema.plain_serializer_function_ser_schema(
                repr, when_used="always"
            ),
        )


class CombinationParams(Protocol):
    api_key: SecretKey
    start_year: int
    end_year: int
    doctype: str
    pubstage: str
    language: str
    open_access: int
    source_type: str
    subject_area: str
    page_range: str
    keywords: list[str]

    @property
    def date(self) -> str:
        pass

    def model_dump(self, **kwargs) -> dict[str, Any]:
        pass


class SurveyParams(CombinationParams):
    combination: str
    ratio: int


class ScopusEntry(Protocol):
    url: str
    scopus_id: str


class ScopusPage(Protocol):
    total_results: int
    items_per_page: int
    entry: list[ScopusEntry]


class ScopusHeaders(Protocol):
    limit: int | None
    remaining: int | None
    reset: int | None
    status: str | None

    @property
    def reset_datetime(self) -> str | None:
        pass

    def model_dump(self, **kwargs) -> dict[str, Any]:
        pass


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
