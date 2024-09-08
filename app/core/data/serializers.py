from datetime import datetime
from math import ceil

from fuzzywuzzy.fuzz import partial_ratio
from pydantic import BaseModel, Field, field_serializer, model_validator

from app.core.common.types import Articles
from app.core.config.scopus import (
    ITEMS_PER_PAGE_FIELD,
    NULL,
    SEARCH_RESULTS_FIELD,
    TOTAL_RESULTS_FIELD,
    RESET_HEADER,
    STATUS_HEADER,
    QUOTA_EXCEEDED,
)


class Article(BaseModel):
    """Serializer for Article JSON schema response"""

    link: str = Field(default=NULL, alias="@_fa", exclude=True)
    url: str = Field(default=NULL, alias="prism:url")
    scopus_id: str = Field(alias="dc:identifier")
    title: str = Field(alias="dc:title")
    publication_name: str = Field(default=NULL, alias="prism:publicationName")
    volume: str = Field(default=NULL, alias="prism:volume")
    date: str = Field(default=NULL, alias="prism:coverDate")
    doi: str = Field(default=NULL, alias="prism:doi")
    citations: str = Field(default=NULL, alias="citedby-count")

    @field_serializer("date")
    def serialize_date(self, date: str):
        try:
            return datetime.strptime(date, "%y-%m-%d").strftime("%d-%m-%y")
        except ValueError:
            return date


class ScopusJSONSchema(BaseModel):
    """Serializer for Scopus Search API JSON schema response"""

    total_results: int = Field(validation_alias=TOTAL_RESULTS_FIELD)
    items_per_page: int = Field(validation_alias=ITEMS_PER_PAGE_FIELD)
    entry: list[Article] = Field()

    @model_validator(mode="before")
    @classmethod
    def flatten_json(cls, data: dict) -> dict:
        return data[SEARCH_RESULTS_FIELD]

    @property
    def pages_count(self) -> int:
        return ceil(self.total_results / self.items_per_page)

    @property
    def articles(self) -> Articles:
        # pylint: disable=E1133
        return [article.model_dump(by_alias=True) for article in self.entry]


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
