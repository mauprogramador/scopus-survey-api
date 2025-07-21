from urllib.parse import urlencode, urljoin

from src.core.common.types import (
    CombinationBundle,
    CombinationParams,
    Keyword,
    SearchParams,
)
from src.core.config.scopus import (
    ARTICLE_PAGE_URL,
    BOOLEAN_OPERATOR,
    QUERY_FIELDS,
    SEARCH_API_URL,
    SEARCH_FIELDS,
)


class URLBuilder:
    """Generate and format URLs for HTTP requests"""

    __SEPARATOR = ","
    __BASE_SEARCH_QUERY = {
        "apiKey": None,
        "query": None,
        "field": "dc:identifier",
        "suppressNavLinks": "true",
        "date": None,
        "start": "0",
        "count": "1",
        "sort": "+pubyear,+coverDate,+relevancy",
    }

    def __init__(self) -> None:
        """Generate and format URLs for HTTP requests"""
        self.__query: dict[str, str | None] = None
        self.__search_terms: str = None

    @staticmethod
    def article_page_url(scopus_id: str) -> str:
        query = {
            "partnerID": "HzOxMe3b",
            "scp": scopus_id,
            "origin": "inward",
        }
        return urljoin(ARTICLE_PAGE_URL, f"?{urlencode(query)}")

    def set_combination_query(self, params: CombinationParams) -> None:
        query_fields = params.model_dump(
            by_alias=True, exclude_unset=True, include=QUERY_FIELDS
        )
        query_terms = {"TITLE-ABS-KEY": "{combination}"}
        query_terms.update(query_fields)

        self.__search_terms = BOOLEAN_OPERATOR.join(
            f"{field}({value})" for field, value in query_terms.items()
        )

        self.__query = self.__BASE_SEARCH_QUERY.copy()
        self.__query["apiKey"] = params.api_key
        self.__query["date"] = params.date
        del self.__query["start"]

    def combination_url(
        self, arrangement: tuple[Keyword, ...]
    ) -> CombinationBundle:
        combination = BOOLEAN_OPERATOR.join(arrangement)

        self.__query["query"] = self.__search_terms.format(
            combination=combination
        )
        url = urljoin(SEARCH_API_URL, f"?{urlencode(self.__query)}")

        return CombinationBundle(combination=combination, url=url)

    def search_url(self, params: SearchParams) -> str:
        query_fields = params.model_dump(
            by_alias=True, exclude_unset=True, include=QUERY_FIELDS
        )
        query_terms = {"TITLE-ABS-KEY": params.combination}
        query_terms.update(query_fields)

        search_terms = BOOLEAN_OPERATOR.join(
            f"{field}({value})" for field, value in query_terms.items()
        )

        self.__query = self.__BASE_SEARCH_QUERY.copy()
        self.__query["apiKey"] = params.api_key
        self.__query["query"] = search_terms
        self.__query["date"] = params.date
        del self.__query["count"]

        return urljoin(SEARCH_API_URL, f"?{urlencode(self.__query)}")

    def pagination_url(self, page: int) -> str:
        self.__query["start"] = page
        return urljoin(SEARCH_API_URL, f"?{urlencode(self.__query)}")

    def set_abstract_query(self, api_key: str) -> None:
        search_fields = self.__SEPARATOR.join(SEARCH_FIELDS)
        self.__query = {"apiKey": api_key, "field": search_fields}

    def abstract_url(self, abstract_url: str) -> str:
        return urljoin(abstract_url, f"?{urlencode(self.__query)}")
