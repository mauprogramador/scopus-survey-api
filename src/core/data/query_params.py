from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    ValidationInfo,
    computed_field,
    field_validator,
)
from pydantic_core import InitErrorDetails, PydanticUseDefault

from src.core.common.types import Keyword
from src.core.config.scopus import (
    CURRENT_YEAR,
    LAST_THREE_YEARS,
    MAX_RECENT_PUBLICATIONS,
)
from src.core.data.enums import (
    Button,
    DocType,
    PageRange,
    PubStage,
    SrcType,
    SubjArea,
)


# e.g. 6bd9327547a3cf4c56586324df4b7d92  (Random Hash)
_API_KEY_PATTERN = r"^[a-zA-Z0-9]{32}$"

# e.g. english, portuguese
_LANGUAGE_PATTERN = r"^[a-z\-\' ]{3,50}$"

# e.g. Python AND "Data Science", COVID-19 OR H2O2
_KEYWORD_COMBINATION_PATTERN = r"^[a-zA-Z0-9\{\}\?\"\*\-\_ ]{2,510}$"


class CSVParams(BaseModel):
    """Validate query params for downloading CSV"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    api_key: str = Field(
        alias="apiKey",
        validation_alias="api_key",
        description="The Scopus API Key issued by Elsevier",
        examples=["439f55d263cj..."],
        pattern=_API_KEY_PATTERN,
        min_length=32,
        max_length=32,
    )
    button: Literal[Button.PREVIOUS, Button.DOWNLOAD] = Field(
        description="The Button-step Action extra context",
        examples=[Button.PREVIOUS],
        exclude=True,
    )


class CombinationParams(CSVParams):
    """Validate query params for survey combinations"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    start_year: int = Field(
        default=LAST_THREE_YEARS,
        alias="startYear",
        validation_alias="start_year",
        description="The Start Year of the Date Range",
        examples=[LAST_THREE_YEARS],
        exclude=True,
        ge=MAX_RECENT_PUBLICATIONS,
        le=(CURRENT_YEAR - 1),
    )
    end_year: int = Field(
        default=CURRENT_YEAR,
        alias="endYear",
        validation_alias="end_year",
        description="The End Year of the Date Range",
        examples=[CURRENT_YEAR],
        exclude=True,
        ge=(MAX_RECENT_PUBLICATIONS + 1),
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
        pattern=_LANGUAGE_PATTERN,
        min_length=3,
        max_length=50,
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
    page_range: PageRange = Field(
        default=None,
        serialization_alias="PAGES",
        description="The documents' size by Page Count",
        examples=[PageRange.SHORT],
    )
    keywords: list[Keyword] = Field(
        description="The Keywords in the documents you are searching for",
        examples=["Python", "Scopus", "Web API", "Bibliographic Survey"],
        exclude=True,
        min_length=1,
        max_length=4,
    )
    button: Literal[Button.COMBINATION] = Field(
        description="The Button-step Action extra context",
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
    def keywords_length(cls, value: Any) -> Any | list[str]:
        if (
            isinstance(value, list)
            and len(value) == 1
            and isinstance(value[0], str)
        ):
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

    @computed_field(return_type=str)  # type: ignore[prop-decorator]
    @property
    def date(self) -> str:
        return f"{self.start_year}-{self.end_year}"


class SearchParams(CombinationParams):
    """Validate query params for survey articles"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    combination: str = Field(
        description="The chosen Keyword Combination to refine the survey",
        examples=["Python AND Machine Learning"],
        exclude=True,
        pattern=_KEYWORD_COMBINATION_PATTERN,
        min_length=2,
        max_length=510,
    )
    ratio: int = Field(
        default=80,
        description="The Filter Ratio used to remove similar documents",
        examples=[80],
        exclude=True,
        ge=0,
        le=100,
    )
    button: Literal[Button.SURVEY] = Field(
        description="The Button-step Action extra context",
        examples=[Button.SURVEY],
        exclude=True,
    )
