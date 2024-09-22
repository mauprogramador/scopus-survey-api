from urllib.parse import quote_plus

from app.core.common.types import Keywords
from app.core.config.scopus import (
    ABSTRACT_API_URL,
    BOOLEAN_OPERATOR,
    DATE_RANGE,
    FIELDS,
    PAGINATION_URL,
    SEARCH_API_URL,
)
from app.core.domain.metaclasses import URLBuilder


class URLBuilderHelper(URLBuilder):
    """Generate and format URLs for HTTP requests"""

    def __init__(self) -> None:
        """Generate and format URLs for HTTP requests"""
        self.__url: str = None

    def get_search_url(self, keywords: Keywords) -> str:
        query = quote_plus(BOOLEAN_OPERATOR.join(keywords))
        self.__url = SEARCH_API_URL.format(query=query, date=DATE_RANGE)
        return self.__url

    def get_pagination_url(self, page: int) -> str:
        return PAGINATION_URL.format(search_url=self.__url, page=page)

    def get_abstract_url(self, url: str) -> str:
        fields = quote_plus(FIELDS)
        return ABSTRACT_API_URL.format(abstract_url=url, fields=fields)
