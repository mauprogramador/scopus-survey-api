from typing import Any, Literal

from fastapi.openapi.models import Example
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
)
from pydantic_core import PydanticUseDefault

from src.core.common.patterns import (
    API_KEY_PATTERN,
    COMBINATION_PATTERN,
    LANGUAGE_PATTERN,
)
from src.core.common.types import Keyword
from src.core.config.config import TOKEN
from src.core.config.scopus import (
    CURRENT_YEAR,
    LAST_DECADE,
    LAST_THREE_YEARS,
    NULL,
)
from src.core.data.enums import Button, DocType, PubStage, SrcType, SubjArea

DESCRIPTION = (
    "The value of the `{TOKEN_HEADER}` header will be"
    " set automatically, you **should not** change it"
)
OPENAPI_EXAMPLE = {
    "Token": Example(
        summary="Access Token", description=DESCRIPTION, value=TOKEN
    )
}


class CSVParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(
        alias="apiKey",
        validation_alias="api_key",
        description="Your Scopus API Key",
        examples=["439f55d263cj..."],
        pattern=API_KEY_PATTERN,
        min_length=32,
        max_length=32,
    )
    csrf_token: str | None = Field(
        default=None,
        alias="csrfToken",
        validation_alias="csrf_token",
        description="The validation CSRF Token",
        examples=["c1d0cf66f682..."],
        exclude=True,
    )
    button: Literal[Button.PREVIOUS, Button.DOWNLOAD] = Field(
        description="Button HTML element",
        examples=[Button.PREVIOUS],
        exclude=True,
    )


class CombinationParams(CSVParams):
    model_config = ConfigDict(extra="forbid")

    start_year: int = Field(
        default=LAST_THREE_YEARS,
        alias="startYear",
        validation_alias="start_year",
        description="Start of search date range",
        examples=[LAST_THREE_YEARS],
        exclude=True,
        ge=LAST_DECADE,
        le=(CURRENT_YEAR - 1),
    )
    end_year: int = Field(
        default=CURRENT_YEAR,
        alias="endYear",
        validation_alias="end_year",
        description="End of search date range",
        examples=[CURRENT_YEAR],
        exclude=True,
        ge=(LAST_DECADE + 1),
        le=CURRENT_YEAR,
    )
    doctype: DocType = Field(
        default=NULL,
        alias="docType",
        validation_alias="doctype",
        serialization_alias="DOCTYPE",
        description="Document type",
        examples=[DocType.AR],
    )
    pubstage: PubStage = Field(
        default=NULL,
        alias="pubStage",
        validation_alias="pubstage",
        serialization_alias="PUBSTAGE",
        description="Publication stage",
        examples=[PubStage.FINAL],
    )
    language: str = Field(
        default=NULL,
        serialization_alias="LANGUAGE",
        description="Language",
        examples=["english"],
        pattern=LANGUAGE_PATTERN,
    )
    open_access: int = Field(
        default=NULL,
        alias="openAccess",
        validation_alias="open_access",
        serialization_alias="OPENACCESS",
        description="Open access",
    )
    source_type: SrcType = Field(
        default=NULL,
        alias="srcType",
        validation_alias="source_type",
        serialization_alias="SRCTYPE",
        description="Source type",
    )
    subject_area: SubjArea = Field(
        default=NULL,
        alias="subjArea",
        validation_alias="subject_area",
        serialization_alias="SUBJAREA",
        description="Subject area",
    )
    pages: int = Field(
        default=NULL, serialization_alias="PAGES", description=""
    )
    keywords: list[Keyword] = Field(
        description="Keywords to search for in the articles",
        examples=["Python"],
        exclude=True,
        min_length=1,
        max_length=4,
    )
    button: Literal[Button.COMBINATION] = Field(
        description="Button HTML element",
        examples=[Button.COMBINATION],
        exclude=True,
    )

    @property
    @computed_field
    def date(self) -> str:
        return f"{self.start_year}-{self.end_year}"

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_default(cls, value: Any) -> Any:
        if isinstance(value, str) and value.strip() == "":
            raise PydanticUseDefault()
        return value

    @field_validator("keywords", mode="before")
    @classmethod
    def keywords_length(cls, value: list[str]) -> list[str]:
        if len(value) == 1:
            return value[0].split(",")
        return value


class SearchParams(CSVParams):
    model_config = ConfigDict(extra="forbid")

    combination: str = Field(
        description="A keywords combination",
        examples=["Python AND Machine Learning"],
        exclude=True,
        pattern=COMBINATION_PATTERN,
        min_length=2,
        max_length=150,
    )
    max_count: int = Field(
        default=125,
        description="Limits the number of returned articles",
        examples=[25],
        exclude=True,
        ge=25,
        le=250,
        multiple_of=25,
    )
    ratio: int = Field(
        default=80,
        description="Filters and removes similar articles",
        examples=[80],
        exclude=True,
        ge=0,
        le=100,
    )
    button: Literal[Button.SEARCH] = Field(
        description="Button HTML element",
        examples=[Button.SEARCH],
        exclude=True,
    )
