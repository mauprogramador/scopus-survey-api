from urllib.parse import quote_plus

from app.core.config.scopus import (
    ABSTRACT_API_URL,
    BOOLEAN_OPERATOR,
    FIELDS,
    PAGINATION_URL,
    SEARCH_API_URL,
)
from app.core.data.query import SearchParams
from app.core.domain.interfaces import URLBuilderABC


class URLBuilder(URLBuilderABC):
    """Generate and format URLs for HTTP requests"""

    def __init__(self) -> None:
        """Generate and format URLs for HTTP requests"""
        self.__url: str = None
        self.__api_key: str = None

    def search_url(self, params: SearchParams) -> str:
        query = quote_plus(BOOLEAN_OPERATOR.join(params.keywords))
        self.__url = SEARCH_API_URL.format(
            apikey=params.api_key,
            query=query,
            date=f"{params.start_year}-{params.end_year}",
            count=params.count,
        )
        return self.__url

    def pagination_url(self, page: int) -> str:
        return PAGINATION_URL.format(search_url=self.__url, page=page)

    def set_abstract_api_key(self, api_key: str) -> None:
        self.__api_key = api_key

    def abstract_url(self, url: str) -> str:
        return ABSTRACT_API_URL.format(
            abstract_url=url,
            apikey=self.__api_key,
            fields=quote_plus(FIELDS),
        )
