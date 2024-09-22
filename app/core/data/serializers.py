from datetime import datetime
from math import ceil

from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)
from thefuzz.fuzz import partial_ratio  # type: ignore

from app.core.config.scopus import (
    NULL,
    QUOTA_EXCEEDED,
    RESET_HEADER,
    STATUS_HEADER,
)


class ScopusResult(BaseModel):
    """Serializer for entry field item in JSON schema response"""

    link: str = Field(default=NULL, alias="@_fa", exclude=True)
    url: str = Field(default=NULL, alias="prism:url")
    scopus_id: str = Field(alias="dc:identifier")


class ScopusSearch(BaseModel):
    """Serializer for Scopus Search API JSON schema response"""

    total_results: int = Field(validation_alias="opensearch:totalResults")
    items_per_page: int = Field(validation_alias="opensearch:itemsPerPage")
    entry: list[ScopusResult] = Field()

    @model_validator(mode="before")
    @classmethod
    def flatten_json(cls, data: dict) -> dict:
        return data["search-results"]

    @property
    def pages_count(self) -> int:
        return ceil(self.total_results / self.items_per_page)


class ScopusHeaders(BaseModel):
    """Serializer for Scopus Search API headers response"""

    reset: float = Field(validation_alias=RESET_HEADER)
    status: str = Field(validation_alias=STATUS_HEADER)

    @property
    def reset_datetime(self) -> str:
        epoch = datetime.fromtimestamp(self.reset)
        return epoch.strftime("%d-%m-%Y at %H:%M:%S")

    @property
    def quota_exceeded(self) -> int:
        return partial_ratio(QUOTA_EXCEEDED, self.status)


class ScopusArticle(BaseModel):
    """Serializer for Abstract Retrieval API JSON schema response"""

    scopus_id: str = Field(
        validation_alias="dc:identifier", serialization_alias="Scopus ID"
    )
    url: str = Field(
        default=NULL,
        validation_alias="link ref=scopus",
        serialization_alias="Article preview page URL",
    )
    eid: str = Field(default=NULL, serialization_alias="Electronic ID")
    title: str = Field(
        validation_alias="dc:title", serialization_alias="Title"
    )
    publication_name: str = Field(
        default=NULL,
        validation_alias="prism:publicationName",
        serialization_alias="Publication Name",
    )
    volume: str = Field(
        default=NULL,
        validation_alias="prism:volume",
        serialization_alias="Volume",
    )
    date: str = Field(
        default=NULL,
        validation_alias="prism:coverDate",
        serialization_alias="Date",
    )
    doi: str = Field(
        default=NULL, validation_alias="prism:doi", serialization_alias="DOI"
    )
    citations: str = Field(
        default=NULL,
        validation_alias="citedby-count",
        serialization_alias="Citations",
    )
    abstract: str = Field(
        default=NULL,
        validation_alias="dc:description",
        serialization_alias="Abstract",
    )
    authors: str = Field(default=NULL, serialization_alias="Authors")

    @model_validator(mode="before")
    @classmethod
    def flatten_json(cls, data: dict) -> dict:
        response: dict[str, dict] = data["abstracts-retrieval-response"]
        if response.get("authors") is None:
            authors_data = {
                "authors": response["coredata"]["dc:creator"]["author"]
            }
        else:
            authors_data = {"authors": response["authors"]["author"]}
        response["coredata"].update(authors_data)
        return response["coredata"]

    @field_validator("authors", mode="before")
    @classmethod
    def get_author_names(cls, data: list[dict]) -> str:
        author_names = [author["ce:indexed-name"] for author in data]
        return ", ".join(author_names)

    @field_serializer("date")
    def serialize_date(self, date: str):
        try:
            return datetime.strptime(date, "%y-%m-%d").strftime("%d-%m-%y")
        except ValueError:
            return date
