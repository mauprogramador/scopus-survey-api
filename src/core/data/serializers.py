from datetime import datetime
from math import ceil

from pydantic import AliasChoices, BaseModel, Field, model_validator

from src.core.common.types import Json
from src.core.config.scopus import ARTICLE_PAGE_URL, NULL


class ScopusEntry(BaseModel):
    """Serializer for entry field item in response JSON schema"""

    link: str = Field(default=NULL, alias="@_fa", exclude=True)
    url: str = Field(default=NULL, alias="prism:url")
    scopus_id: str = Field(validation_alias="dc:identifier")


class ScopusSearch(BaseModel):
    """Serializer for Scopus Search API response JSON schema"""

    total_results: int = Field(validation_alias="opensearch:totalResults")
    items_per_page: int = Field(validation_alias="opensearch:itemsPerPage")
    entry: list[ScopusEntry] = Field()

    @model_validator(mode="before")
    @classmethod
    def flatten_json(cls, data: Json) -> Json:
        return data["search-results"]

    def count_limit(self, count: int) -> None:
        self.total_results = min(self.total_results, count)

    @property
    def pages_count(self) -> int:
        return ceil(self.total_results / self.items_per_page)


class ScopusAbstract(BaseModel):
    """Serializer for Scopus Abstract Retrieval API response JSON schema"""

    url: str = Field(
        default=NULL,
        validation_alias="prism:url",
        serialization_alias="Article Preview Page URL",
    )
    scopus_id: str = Field(
        validation_alias="dc:identifier", serialization_alias="Scopus ID"
    )
    authors: str = Field(
        default=NULL,
        serialization_alias="Authors",
    )
    title: str = Field(
        validation_alias="dc:title", serialization_alias="Title"
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
        url = ARTICLE_PAGE_URL.format(scopus_id=scopus_id)

        data["coredata"].setdefault("authors", ", ".join(authors_names))
        data["coredata"].setdefault("prism:url", url)

        return data["coredata"]


class ScopusQuotaRateLimit(BaseModel):
    """Serializer for Scopus APIs response headers"""

    limit: int = Field(default=NULL, validation_alias="X-RateLimit-Limit")
    remaining: int = Field(
        default=NULL, validation_alias="X-RateLimit-Remaining"
    )
    reset: int = Field(default=NULL, validation_alias="X-RateLimit-Reset")
    status: str = Field(default=NULL, validation_alias="X-ELS-Status")

    @property
    def reset_datetime(self) -> str:
        if self.reset == NULL:
            return NULL
        epoch = datetime.fromtimestamp(self.reset)
        return epoch.strftime("%Y-%m-%d %H:%M:%S")


class ScopusErrorResponse(BaseModel):
    """Serializer for Scopus APIs error responses"""

    code: str = Field(
        default=NULL,
        validation_alias=AliasChoices("error-code", "statusCode"),
    )

    @model_validator(mode="before")
    @classmethod
    def flatten_json(cls, json: Json) -> dict[str, str]:
        if json.get("error-response") is not None:
            return json["error-response"]
        if json.get("service-error") is not None:
            return json["service-error"]["status"]
        return json
