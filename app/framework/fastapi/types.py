from fastapi import Header, Query

from app.core.common.patterns import API_KEY_PATTERN, TOKEN_PATTERN
from app.core.config.config import (
    API_KEY_QUERY,
    KEYWORDS_QUERY,
    TOKEN_HEADER,
)
from app.core.config.scopus import CURRENT_YEAR, LAST_DECADE
from app.framework.fastapi.config import OPENAPI_EXAMPLE


TokenHeader: str = Header(
    alias=TOKEN_HEADER,
    description="The validation Access Token",
    min_length=32,
    max_length=32,
    pattern=TOKEN_PATTERN,
    openapi_examples=OPENAPI_EXAMPLE,
)

APIKeyQuery: str = Query(
    alias=API_KEY_QUERY,
    description="Your Scopus API Key",
    min_length=32,
    max_length=32,
    pattern=API_KEY_PATTERN,
)

KeywordsQuery: list[str] = Query(
    alias=KEYWORDS_QUERY,
    description="Keywords to search for in the articles",
    min_length=1,
    max_length=4,
)

CountQuery: int = Query(
    alias="count",
    description="",
    ge=1,
    le=200,
    decimal_places=None,
)

ThresholdQuery: int = Query(
    # default=0,
    alias="threshold",
    description="",
    ge=0,
    le=100,
    decimal_places=None,
)

StartYearQuery: int = Query(
    # default=LAST_THREE_YEARS,
    alias="Start Year",
    description="",
    ge=LAST_DECADE,
    le=(CURRENT_YEAR - 1),
    decimal_places=None,
)

EndYearQuery: int = Query(
    # default=CURRENT_YEAR,
    alias="Start Year",
    description="",
    ge=(LAST_DECADE + 1),
    le=CURRENT_YEAR,
    decimal_places=None,
)
