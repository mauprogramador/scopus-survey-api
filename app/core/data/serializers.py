from datetime import datetime
from math import ceil

from pydantic import (
    BaseModel,
    Field,
    AliasChoices,
    field_validator,
    model_validator,
)

from app.core.config.config import CSV_HEADER, USER_API_KEY_HEADER
from app.core.config.scopus import ARTICLE_PAGE_URL, NULL


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
    """Serializer for Scopus APIs response headers"""

    limit: int = Field(default=NULL, validation_alias="X-RateLimit-Limit")
    remaining: int = Field(
        default=NULL, validation_alias="X-RateLimit-Remaining"
    )
    reset: int = Field(default=NULL, validation_alias="X-RateLimit-Reset")
    status: str = Field(default=NULL, validation_alias="X-ELS-Status")

    @property
    def reset_datetime(self) -> str:
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
    def flatten_json(cls, json: dict) -> dict:
        if json.get("error-response") is not None:
            return json["error-response"]
        if json.get("service-error") is not None:
            return json["service-error"]["status"]
        return json


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
    def join_author_names(cls, data: list[dict]) -> str:
        author_names = [author["ce:indexed-name"] for author in data]
        return ", ".join(author_names)


class CSVFileHeaders(BaseModel):
    """Serializer for csv file response headers"""

    content_disposition: str = Field(serialization_alias="Content-Disposition")
    content_type: str = Field(
        default="text/csv; charset=utf-8", serialization_alias="Content-Type"
    )
    x_csv_filename: str = Field(serialization_alias=CSV_HEADER)
    x_user_api_key: str = Field(serialization_alias=USER_API_KEY_HEADER)

    @staticmethod
    def build(filename: str, api_key: str) -> dict[str, str]:
        disposition = f"attachment; filename={filename}"

        headers = CSVFileHeaders(
            content_disposition=disposition,
            x_csv_filename=filename,
            x_user_api_key=api_key,
        )

        return headers.model_dump(by_alias=True)
