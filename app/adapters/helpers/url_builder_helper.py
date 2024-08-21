from urllib.parse import quote_plus

from app.core.common.types import Keywords
from app.core.config.scopus import (
    API_URL,
    ARTICLE_PAGE_URL,
    BOOLEAN_OPERATOR,
    DATE_RANGE,
    FIELDS,
    PAGINATION_SUFFIX,
)
from app.core.domain.metaclasses import UrlBuilder


class UrlBuilderHelper(UrlBuilder):
    """Generate and format URLs for HTTP requests"""

    __SEP = ":"

    def __init__(self) -> None:
        """Generate and format URLs for HTTP requests"""
        self.__url: str = None

    def get_search_url(self, keywords: Keywords) -> str:
        query = quote_plus(BOOLEAN_OPERATOR.join(keywords))
        self.__url = API_URL.format(
            query=query, fields=FIELDS, date=DATE_RANGE
        )
        return self.__url

    def get_pagination_url(self, page: int) -> str:
        return f"{self.__url}{PAGINATION_SUFFIX}{page}"

    def get_article_page_url(self, scopus_id: str) -> str:
        scopus_id = scopus_id.split(self.__SEP)[1]
        return ARTICLE_PAGE_URL.format(scopus_id=scopus_id)
