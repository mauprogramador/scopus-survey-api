from datetime import datetime
from math import ceil
from typing import Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from src.adapters.helpers.url_builder import URLBuilder
from src.core.common.patterns import ABSTRACT_URL_PATTERN, SCOPUS_ID_PATTERN
from src.core.common.types import Json
from src.core.config.scopus import EMPTY_RESULT, NULL


class ScopusEntry(BaseModel):
    """Serialize the entry field in the JSON response"""

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    force_array: Literal["true"] = Field(validation_alias="@_fa", exclude=True)
    url: str = Field(
        default=NULL,
        validation_alias="prism:url",
        pattern=ABSTRACT_URL_PATTERN,
        min_length=61,
        max_length=70,
    )
    scopus_id: str = Field(
        validation_alias="dc:identifier",
        pattern=SCOPUS_ID_PATTERN,
        min_length=20,
        max_length=29,
    )


class ScopusSearch(BaseModel):
    """Serialize the Scopus Search API JSON response"""

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    total_results: int = Field(
        validation_alias="opensearch:totalResults", ge=0
    )
    items_per_page: int = Field(
        validation_alias="opensearch:itemsPerPage", ge=0, le=25
    )
    entry: list[ScopusEntry] = Field(min_length=1, max_length=25)

    @model_validator(mode="before")
    @classmethod
    def flatten_json(cls, data: Json) -> Json:
        return data["search-results"]

    @field_validator("entry", mode="before")
    @classmethod
    def validate_entry(cls, data: list[Json]) -> list[Json]:
        if len(data) == 1 and data[0].get("error") == EMPTY_RESULT:
            data[0].update({"dc:identifier": "SCOPUS_ID:0123456789"})
        return data

    def set_count_limit(self, count: int) -> None:
        self.total_results = min(self.total_results, count)

    @property
    def pages_count(self) -> int:
        return ceil(self.total_results / self.items_per_page)


class ScopusAbstract(BaseModel):
    """Serialize the Scopus Abstract Retrieval API JSON response"""

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    url: str = Field(
        default=NULL,
        validation_alias="prism:url",
        serialization_alias="Article Preview Page URL",
        min_length=77,
    )
    scopus_id: str = Field(
        validation_alias="dc:identifier",
        serialization_alias="Scopus ID",
        pattern=SCOPUS_ID_PATTERN,
        min_length=20,
        max_length=29,
    )
    authors: str = Field(
        default=NULL,
        serialization_alias="Authors",
    )
    title: str = Field(
        validation_alias="dc:title", serialization_alias="Title", min_length=1
    )
    publication_name: str = Field(
        default=NULL,
        validation_alias="prism:publicationName",
        serialization_alias="Publication Name",
    )
    abstract: str = Field(
        default=NULL,
        validation_alias="dc:description",
        serialization_alias="Abstract",
    )
    date: str = Field(
        default=NULL,
        validation_alias="prism:coverDate",
        serialization_alias="Date",
    )
    eid: str = Field(default=NULL, serialization_alias="Electronic ID")
    doi: str = Field(
        default=NULL, validation_alias="prism:doi", serialization_alias="DOI"
    )
    volume: str = Field(
        default=NULL,
        validation_alias="prism:volume",
        serialization_alias="Volume",
    )
    citations: str = Field(
        default=NULL,
        validation_alias="citedby-count",
        serialization_alias="Citations",
    )

    @model_validator(mode="before")
    @classmethod
    def flatten_json(cls, response: Json) -> Json:
        data: dict[str, Json] = response["abstracts-retrieval-response"]

        if data.get("authors") is None:
            authors: list[Json] = data["coredata"]["dc:creator"]["author"]
        else:
            authors: list[Json] = data["authors"]["author"]

        authors_names = [author["ce:indexed-name"] for author in authors]
        identifier: str = data["coredata"]["dc:identifier"]

        scopus_id: str = identifier.split(":")[1]
        url = URLBuilder.article_page_url(scopus_id)

        data["coredata"].setdefault("authors", ", ".join(authors_names))
        data["coredata"].setdefault("prism:url", url)

        return data["coredata"]


class ScopusQuotaRateLimit(BaseModel):
    """Serialize the Scopus APIs response headers"""

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    limit: int = Field(
        default=NULL, validation_alias="X-RateLimit-Limit", ge=0
    )
    remaining: int = Field(
        default=NULL, validation_alias="X-RateLimit-Remaining", ge=0
    )
    reset: int = Field(validation_alias="X-RateLimit-Reset", ge=0)
    status: str = Field(validation_alias="X-ELS-Status", min_length=1)

    @property
    def reset_datetime(self) -> str:
        epoch = datetime.fromtimestamp(self.reset)
        return epoch.strftime("%Y-%m-%d %H:%M:%S")


class ScopusErrorResponse(BaseModel):
    """Serialize the Scopus APIs error responses"""

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    code: str = Field(
        default=NULL,
        validation_alias=AliasChoices("error-code", "statusCode"),
        min_length=1,
    )

    @model_validator(mode="before")
    @classmethod
    def flatten_json(cls, json: Json) -> dict[str, str]:
        if json.get("error-response") is not None:
            return json["error-response"]

        if json.get("service-error") is not None:
            return json["service-error"]["status"]

        return json
