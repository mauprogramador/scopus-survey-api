from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    ValidationInfo,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)
from pydantic_core import InitErrorDetails, PydanticUseDefault

from src.core.common.patterns import (
    API_KEY_PATTERN,
    COMBINATION_PATTERN,
    LANGUAGE_PATTERN,
)
from src.core.common.types import Json, Keyword
from src.core.config.scopus import (
    CURRENT_YEAR,
    LAST_DECADE,
    LAST_THREE_YEARS,
    PAGE_RANGE,
)
from src.core.data.enums import (
    Button,
    DocType,
    PageRange,
    PubStage,
    SrcType,
    SubjArea,
)


class CSVParams(BaseModel):
    """Validate query params for downloading CSV"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    api_key: str = Field(
        alias="apiKey",
        validation_alias="api_key",
        description="Your Scopus API Key",
        examples=["439f55d263cj..."],
        pattern=API_KEY_PATTERN,
        min_length=32,
        max_length=32,
    )
    button: Literal[Button.PREVIOUS, Button.DOWNLOAD] = Field(
        description="The HTML button value",
        examples=[Button.PREVIOUS],
        exclude=True,
    )

    @model_validator(mode="before")
    @classmethod
    def auto_remove_token_from_query(cls, data: Json) -> Json:
        data.pop("csrfToken", None)
        data.pop("csrf_token", None)
        return data


class CombinationParams(CSVParams):
    """Validate query params for survey combinations"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    start_year: int = Field(
        default=LAST_THREE_YEARS,
        alias="startYear",
        validation_alias="start_year",
        description="Date range start year",
        examples=[LAST_THREE_YEARS],
        exclude=True,
        ge=LAST_DECADE,
        le=(CURRENT_YEAR - 1),
    )
    end_year: int = Field(
        default=CURRENT_YEAR,
        alias="endYear",
        validation_alias="end_year",
        description="Date range end year",
        examples=[CURRENT_YEAR],
        exclude=True,
        ge=(LAST_DECADE + 1),
        le=CURRENT_YEAR,
    )
    doctype: DocType = Field(
        default=None,
        alias="docType",
        validation_alias="doctype",
        serialization_alias="DOCTYPE",
        description="The Document Type in which the document is classified",
        examples=[DocType.AR],
    )
    pubstage: PubStage = Field(
        default=None,
        alias="pubStage",
        validation_alias="pubstage",
        serialization_alias="PUBSTAGE",
        description="The Publication Stage of the document",
        examples=[PubStage.FINAL],
    )
    language: str = Field(
        default=None,
        serialization_alias="LANGUAGE",
        description="The Language in which the document was written",
        examples=["english"],
        pattern=LANGUAGE_PATTERN,
        min_length=3,
        max_length=30,
    )
    open_access: Literal["0", "1"] = Field(
        default=None,
        alias="openAccess",
        validation_alias="open_access",
        serialization_alias="OPENACCESS",
        description="Whether the indexed content is Open Access or not",
        examples=[0],
    )
    source_type: SrcType = Field(
        default=None,
        alias="srcType",
        validation_alias="source_type",
        serialization_alias="SRCTYPE",
        description="The Source Type the document comes from",
        examples=[SrcType.J],
    )
    subject_area: SubjArea = Field(
        default=None,
        alias="subjArea",
        validation_alias="subject_area",
        serialization_alias="SUBJAREA",
        description="The Subject Area in which the document is classified",
        examples=[SubjArea.COMP],
    )
    pages: PageRange = Field(
        default=None,
        serialization_alias="PAGES",
        description="The page number range to filter documents",
        examples=[PageRange.SHORT.name],
    )
    keywords: list[Keyword] = Field(
        description="The Keywords to search for in the documents fields",
        examples=["Python,Machine Learning"],
        exclude=True,
        min_length=1,
        max_length=4,
    )
    button: Literal[Button.COMBINATION] = Field(
        description="The HTML button value",
        examples=[Button.COMBINATION],
        exclude=True,
    )

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_default(cls, value: Any, info: ValidationInfo) -> Any:
        field = cls.model_fields.get(info.field_name)
        if field:
            invalid_value = isinstance(value, str) and value.strip() == ""
            if not field.is_required() and invalid_value:
                raise PydanticUseDefault()
        return value

    @field_validator("keywords", mode="before")
    @classmethod
    def keywords_length(cls, value: list[str]) -> list[str]:
        if len(value) == 1:
            keywords = value[0].split(",")
            if len(keywords) < 2:
                raise ValidationError.from_exception_data(
                    "Keywords length too short",
                    [
                        InitErrorDetails(
                            type="too_short",
                            input=value,
                            ctx={
                                "field_type": "List",
                                "min_length": 2,
                                "actual_length": len(keywords),
                            },
                        )
                    ],
                )
            return keywords
        return value

    @field_serializer("pages", return_type=str)
    def serialize_page_range(self, value: PageRange | None) -> str | None:
        return None if value is None else PAGE_RANGE[value]

    @computed_field(  # type: ignore[prop-decorator]
        description="Date range by years",
        examples=[f"{LAST_THREE_YEARS}-{CURRENT_YEAR}"],
    )
    @property
    def date(self) -> str:
        return f"{self.start_year}-{self.end_year}"


class SearchParams(CombinationParams):
    """Validate query params for survey articles"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    combination: str = Field(
        description="The chosen keywords combination",
        examples=["Python AND Machine Learning"],
        exclude=True,
        pattern=COMBINATION_PATTERN,
        min_length=2,
        max_length=215,
    )
    max_count: int = Field(
        default=125,
        description="Limits the number of returned documents",
        examples=[25],
        exclude=True,
        ge=25,
        le=250,
        multiple_of=25,
    )
    ratio: int = Field(
        default=80,
        description="Filter ratio to remove similar documents",
        examples=[80],
        exclude=True,
        ge=0,
        le=100,
    )
    button: Literal[Button.SEARCH] = Field(
        description="The HTML button value",
        examples=[Button.SEARCH],
        exclude=True,
    )
