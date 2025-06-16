from urllib.parse import quote_plus

from src.core.common.types import SearchParams
from src.core.config.scopus import (
    ABSTRACT_API_URL,
    BOOLEAN_OPERATOR,
    FIELDS,
    PAGINATION_URL,
    SEARCH_API_URL,
)
from src.core.domain.interfaces import URLBuilderABC


class URLBuilder(URLBuilderABC):
    """Generate and format URLs for HTTP requests"""

    def __init__(self) -> None:
        """Generate and format URLs for HTTP requests"""
        self.__search_url: str = None
        self.__api_key: str = None

    def search_url(self, params: SearchParams) -> str:
        keywords = quote_plus(BOOLEAN_OPERATOR.join(params.keywords))
        self.__search_url = SEARCH_API_URL.format(
            apikey=params.api_key,
            keywords=keywords,
            date=params.year_range,
        )
        return self.__search_url

    def pagination_url(self, page: int) -> str:
        return PAGINATION_URL.format(search_url=self.__search_url, page=page)

    def set_abstract_api_key(self, api_key: str) -> None:
        self.__api_key = api_key

    def abstract_url(self, abstract_url: str) -> str:
        return ABSTRACT_API_URL.format(
            abstract_url=abstract_url,
            apikey=self.__api_key,
            fields=quote_plus(FIELDS),
        )
