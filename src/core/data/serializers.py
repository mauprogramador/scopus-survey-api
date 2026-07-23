import math
from datetime import datetime
from typing import Literal, Self

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from src.adapters.helpers.url_builder import build_article_page_url
from src.core.common.types import Json
from src.core.config.scopus import EMPTY_RESULT


# e.g. http://api.elsevier.com/content/abstract/scopus_id/0123456789
_ABSTRACT_URL_PATTERN = (
    r"^https\:\/\/api\.elsevier\.com\/content\/abstract"
    r"\/scopus_id\/[0-9]{10,}$"
)

# e.g. SCOPUS_ID:0123456789
_SCOPUS_ID_PATTERN = r"^SCOPUS_ID\:[0-9]{10,}$"


class ScopusEntry(BaseModel):
    """Serialize the entry field in the JSON response"""

    model_config = ConfigDict(str_strip_whitespace=True)

    force_array: Literal["true"] = Field(
        validation_alias="@_fa",
        exclude=True,
    )
    url: str = Field(
        validation_alias="prism:url",
        pattern=_ABSTRACT_URL_PATTERN,
        min_length=61,
        max_length=70,
    )
    scopus_id: str = Field(
        validation_alias="dc:identifier",
        pattern=_SCOPUS_ID_PATTERN,
        min_length=20,
        max_length=29,
    )


class ScopusPage(BaseModel):
    """Serialize the Scopus Search API JSON response"""

    model_config = ConfigDict(str_strip_whitespace=True)

    total_results: int = Field(validation_alias="opensearch:totalResults")
    items_per_page: int = Field(validation_alias="opensearch:itemsPerPage")
    entry: list[ScopusEntry] = Field()

    @model_validator(mode="before")
    @classmethod
    def flatten_json(cls, data: Json) -> Json:
        return data["search-results"]

    @field_validator("entry", mode="before")
    @classmethod
    def validate_entry(cls, data: list[Json]) -> list[Json]:
        if len(data) == 1 and data[0].get("error") == EMPTY_RESULT:
            return []
        return data

    @property
    def pages_count(self) -> int:
        if self.total_results == 0:
            return 0
        return math.ceil(self.total_results / self.items_per_page)


class ScopusAbstract(BaseModel):
    """Serialize the Scopus Abstract Retrieval API JSON response"""

    model_config = ConfigDict(str_strip_whitespace=True)

    url: str = Field(default=None)
    scopus_id: str = Field(
        validation_alias="dc:identifier",
        pattern=_SCOPUS_ID_PATTERN,
        min_length=20,
        max_length=29,
    )
    authors: str | None = Field(default=None)
    title: str = Field(validation_alias="dc:title")
    publication_name: str | None = Field(
        default=None, validation_alias="prism:publicationName"
    )
    abstract: str | None = Field(
        default=None, validation_alias="dc:description"
    )
    date: str | None = Field(default=None, validation_alias="prism:coverDate")
    eid: str | None = Field(default=None)
    doi: str | None = Field(default=None, validation_alias="prism:doi")
    volume: str | None = Field(default=None, validation_alias="prism:volume")
    citations: str | None = Field(
        default=None, validation_alias="citedby-count"
    )

    @model_validator(mode="before")
    @classmethod
    def flatten_json_and_set_authors(cls, data: Json) -> Json:
        data: dict[str, Json] = data["abstracts-retrieval-response"]

        if data.get("authors") is None:
            coredata = data["coredata"]

            if coredata.get("dc:creator") is None:
                authors = [{"ce:indexed-name": NULL}]
            else:
                authors: list[Json] = coredata["dc:creator"]["author"]
        else:
            authors: list[Json] = data["authors"]["author"]

        authors_names = [author["ce:indexed-name"] for author in authors]
        data["coredata"].setdefault("authors", ", ".join(authors_names))

        return data["coredata"]

    @model_validator(mode="after")
    def set_article_page_url(self) -> Self:
        scopus_id = self.scopus_id.split(":")[1]  # pylint: disable=E1101
        self.url = build_article_page_url(scopus_id)
        return self


class ScopusHeaders(BaseModel):
    """Serialize the Scopus APIs response headers"""

    model_config = ConfigDict(str_strip_whitespace=True)

    limit: int | None = Field(
        default=None, validation_alias="X-RateLimit-Limit"
    )
    remaining: int | None = Field(
        default=None, validation_alias="X-RateLimit-Remaining"
    )
    reset: int | None = Field(
        default=None, validation_alias="X-RateLimit-Reset"
    )
    status: str | None = Field(default=None, validation_alias="X-ELS-Status")

    @computed_field(return_type=str)  # type: ignore[prop-decorator]
    @property
    def reset_datetime(self) -> str:
        if self.reset is None:
            return None
        epoch = datetime.fromtimestamp(self.reset)
        return epoch.strftime("%Y-%m-%d %H:%M:%S")  # e.g. 2026-01-01 00:00:00


class ScopusError(BaseModel):
    """Serialize the Scopus APIs error responses"""

    model_config = ConfigDict(str_strip_whitespace=True)

    code: str = Field(
        validation_alias=AliasChoices("error-code", "statusCode")
    )
    text: str = Field(
        validation_alias=AliasChoices("error-message", "statusText")
    )

    @model_validator(mode="before")
    @classmethod
    def flatten_json(cls, data: Json) -> dict[str, str]:
        if data.get("error-response") is not None:
            return data["error-response"]

        if data.get("service-error") is not None:
            return data["service-error"]["status"]

        return data
