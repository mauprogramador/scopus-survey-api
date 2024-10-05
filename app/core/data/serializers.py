from datetime import datetime
from math import ceil

from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)
from requests import Response

from app.core.config.scopus import (
    ARTICLE_PAGE_URL,
    NULL,
    QUOTA_EXCEEDED,
    RATE_LIMIT_EXCEEDED,
)


class ScopusResult(BaseModel):
    """Serializer for entry field item in response JSON schema"""

    link: str = Field(default=NULL, alias="@_fa")
    url: str = Field(default=NULL, alias="prism:url")
    scopus_id: str = Field(alias="dc:identifier")


class ScopusSearch(BaseModel):
    """Serializer for Scopus Search API response JSON schema"""

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


class ScopusQuotaRateLimit(BaseModel):
    """Serializer for Scopus APIs responses"""

    reset: float = Field(default=NULL, validation_alias="X-RateLimit-Reset")
    status: str = Field(default=NULL, validation_alias="X-ELS-Status")
    error_code: str = Field(default=NULL, validation_alias="error-code")

    @model_validator(mode="before")
    @classmethod
    def flatten_json(cls, response: Response) -> dict:
        model_data: dict = {}
        content: dict = response.json()
        model_data.update(response.headers)
        if content.get("error-response"):
            model_data.update(content["error-response"])
        return model_data

    @property
    def reset_datetime(self) -> str:
        epoch = datetime.fromtimestamp(self.reset)
        return epoch.strftime("%d-%m-%Y at %H:%M:%S")

    @property
    def quota_exceeded(self) -> bool:
        return self.status == QUOTA_EXCEEDED

    @property
    def rate_limit_exceeded(self) -> bool:
        return self.error_code == RATE_LIMIT_EXCEEDED


class ScopusAbstract(BaseModel):
    """Serializer for Scopus Abstract Retrieval API response JSON schema"""

    url: str = Field(
        default=NULL,
        serialization_alias="Article Preview Page URL",
    )
    scopus_id: str = Field(
        validation_alias="dc:identifier", serialization_alias="Scopus ID"
    )
    authors: str = Field(default=NULL, serialization_alias="Authors")
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
    def flatten_json(cls, data: dict) -> dict:
        response: dict[str, dict] = data["abstracts-retrieval-response"]
        if response.get("authors") is None:
            authors_data = {
                "authors": response["coredata"]["dc:creator"]["author"]
            }
        else:
            authors_data = {"authors": response["authors"]["author"]}
        identifier: str = response["coredata"]["dc:identifier"]
        scopus_id: str = identifier.split(":")[1]
        url = {"url": ARTICLE_PAGE_URL.format(scopus_id=scopus_id)}
        response["coredata"].update(authors_data)
        response["coredata"].update(url)
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
