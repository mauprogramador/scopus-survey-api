from fastapi import Header, Query

from app.core.common.patterns import API_KEY_PATTERN, TOKEN_PATTERN
from app.core.common.types import Keywords
from app.core.config.config import (
    API_KEY_HEADER,
    KEYWORDS_HEADER,
    TOKEN_HEADER,
)
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
    alias=API_KEY_HEADER,
    description="Your Scopus API Key",
    min_length=32,
    max_length=32,
    pattern=API_KEY_PATTERN,
)

KeywordsQuery: Keywords = Query(
    alias=KEYWORDS_HEADER,
    description="Keywords to search for in the articles",
    min_length=1,
    max_length=4,
)
