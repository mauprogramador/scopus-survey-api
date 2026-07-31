from datetime import datetime
from typing import Any, Literal, Self

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from src.core.domain.types import Json
from src.infra.config.scopus import EMPTY_RESULT
from src.infra.http.url_builder import build_article_page_url


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
    def flatten_json(cls, data: Any) -> Any | Json:
        try:
            return data["search-results"]

        except (KeyError, TypeError):
            return data

    @field_validator("entry", mode="before")
    @classmethod
    def validate_entry(cls, value: Any) -> Any | list:
        try:
            if value[0]["error"] == EMPTY_RESULT:
                return []

        except (KeyError, TypeError):
            pass

        return value


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
    def flatten_json_and_set_authors(cls, data: Any) -> Any | Json:
        try:
            res: dict[str, Json] = data["abstracts-retrieval-response"]
            core_data = res["coredata"]

            if "authors" in res:
                authors: list[Json] = res["authors"]["author"]

            elif "dc:creator" in core_data:
                authors: list[Json] = core_data["dc:creator"]["author"]

            else:
                return core_data

            authors_names = [author["ce:indexed-name"] for author in authors]
            core_data["authors"] = ", ".join(authors_names)

            return core_data

        except (KeyError, TypeError):
            return data

    @model_validator(mode="after")
    def set_article_page_url(self) -> Self:
        # Pylint gets 'FieldInfo' instead of 'str'
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

    @computed_field  # type: ignore[prop-decorator]
    @property
    def reset_datetime(self) -> str | None:
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
    def flatten_json(cls, data: Any) -> dict[str, str]:
        try:
            if "error-response" in data:
                return data["error-response"]

            if "service-error" in data:
                return data["service-error"]["status"]

        except (KeyError, TypeError):
            pass

        return data
