from typing import Any, Literal, cast

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    computed_field,
    field_validator,
)
from pydantic_core import PydanticUseDefault

from src.adapters.types import (
    Button,
    DocType,
    Keyword,
    PageRange,
    PubStage,
    SrcType,
    SubjArea,
)
from src.core.domain.types import SecretKey
from src.infra.config.scopus import (
    CURRENT_YEAR,
    LAST_THREE_YEARS,
    MAX_RECENT_PUBLICATIONS,
)


class CSVParams(BaseModel):
    """Validate query params for downloading CSV"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    # e.g. 6bd9327547a3cf4c56586324df4b7d92  (Random Hash)
    api_key: SecretKey = Field(
        alias="apiKey",
        validation_alias="api_key",
        description="The Scopus API Key issued by Elsevier",
        examples=["439f55d263cj..."],
        pattern=r"^[a-zA-Z0-9]{32}$",
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
    doctype: DocType | None = Field(
        default=None,
        alias="docType",
        validation_alias="doctype",
        serialization_alias="DOCTYPE",
        description="The Document Type in which the document is classified",
        examples=[DocType.AR],
    )
    pubstage: PubStage | None = Field(
        default=None,
        alias="pubStage",
        validation_alias="pubstage",
        serialization_alias="PUBSTAGE",
        description="The Publication Stage of the document",
        examples=[PubStage.FINAL],
    )
    # e.g. english, portuguese
    language: str | None = Field(
        default=None,
        serialization_alias="LANGUAGE",
        description="The Language in which the document was written",
        examples=["english"],
        pattern=r"^[a-z\-\' ]{3,50}$",
        min_length=3,
        max_length=50,
    )
    open_access: Literal["0", "1"] | None = Field(
        default=None,
        alias="openAccess",
        validation_alias="open_access",
        serialization_alias="OPENACCESS",
        description="Whether the indexed content is Open Access or not",
        examples=[0],
    )
    source_type: SrcType | None = Field(
        default=None,
        alias="srcType",
        validation_alias="source_type",
        serialization_alias="SRCTYPE",
        description="The Source Type the document comes from",
        examples=[SrcType.J],
    )
    subject_area: SubjArea | None = Field(
        default=None,
        alias="subjArea",
        validation_alias="subject_area",
        serialization_alias="SUBJAREA",
        description="The Subject Area in which the document is classified",
        examples=[SubjArea.COMP],
    )
    page_range: PageRange | None = Field(
        default=None,
        serialization_alias="PAGES",
        description="The documents' size by Page Count",
        examples=[PageRange.SHORT],
    )
    keywords: list[Keyword] = Field(
        description="The Keywords in the documents you are searching for",
        examples=["Python", "Scopus", "Web API", "Bibliographic Survey"],
        min_length=2,
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
            has_empty_value = isinstance(value, str) and value.strip() == ""

            if not field.is_required() and has_empty_value:
                raise PydanticUseDefault()

        return value

    @field_validator("keywords", mode="before")
    @classmethod
    def handle_keywords_length(cls, value: Any) -> Any | list[str]:
        if isinstance(value, str):
            return [keyword.strip() for keyword in value.split(",")]

        try:
            value: list[str] = cast(list[str], value)

            if len(value) == 1:
                return [keyword.strip() for keyword in value[0].split(",")]

        except (KeyError, TypeError):
            pass

        return value

    @computed_field  # type: ignore[prop-decorator]
    @property
    def date(self) -> str:
        return f"{self.start_year}-{self.end_year}"


class SurveyParams(CombinationParams):
    """Validate query params for survey articles"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    # e.g. Python AND "Data Science", COVID-19 OR H2O2
    combination: str = Field(
        description="The chosen Keyword Combination to refine the survey",
        examples=["Python AND Machine Learning"],
        pattern=r"^[a-zA-Z0-9\{\}\?\"\*\-\_ ]{2,510}$",
        min_length=2,
        max_length=510,  # 4x Keywords + AND operator
    )
    ratio: int = Field(
        default=80,
        description="The Filter Ratio used to remove similar documents",
        examples=[80],
        ge=0,
        le=100,
    )
    button: Literal[Button.SURVEY] = Field(
        description="The Button-step Action extra context",
        examples=[Button.SURVEY],
        exclude=True,
    )
