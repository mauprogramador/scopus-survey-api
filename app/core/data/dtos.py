from pydantic import BaseModel, Field, field_validator

from app.core.common.messages import INVALID_KEYWORD
from app.core.common.patterns import API_KEY_PATTERN, KEYWORD_PATTERN
from app.core.common.types import Keywords


class SearchParams(BaseModel):
    """Type validator for APIKey and Keywords search params"""

    api_key: str = Field(min_length=32, max_length=32, pattern=API_KEY_PATTERN)
    keywords: Keywords = Field(min_length=2, max_length=4)

    @field_validator("keywords")
    @classmethod
    def validate_keywords(cls, keywords: Keywords) -> Keywords:
        for keyword in keywords:
            if not KEYWORD_PATTERN.match(keyword):
                raise ValueError(INVALID_KEYWORD)
        return keywords
