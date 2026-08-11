from collections.abc import Callable
from urllib.parse import urlencode

from src.core.domain.types import (
    CombinationParams,
    SurveyParams,
)
from src.infra.config.scopus import (
    ARTICLE_PAGE_URL,
    BOOLEAN_OPERATOR,
    QUERY_FIELDS,
    SEARCH_API_URL,
    SEARCH_FIELDS,
)
from src.infra.utils import logger


_FIELDS = ",".join(SEARCH_FIELDS)
_BASE_QUERY_PARAMS = {
    "apiKey": None,
    "query": None,
    "field": "dc:identifier",
    "suppressNavLinks": "true",
    "date": None,
    "start": "0",
    "count": "1",
    "sort": "+pubyear,+coverDate,+relevancy",
}


def build_article_page_url(scopus_id: str) -> str:
    query = {
        "partnerID": "HzOxMe3b",
        "scp": scopus_id,
        "origin": "inward",
    }
    return f"{ARTICLE_PAGE_URL}?{urlencode(query)}"


def build_combination_urls(params: CombinationParams) -> Callable[[str], str]:
    query_fields = params.model_dump(
        by_alias=True,
        exclude_unset=True,
        exclude_none=True,
        include=QUERY_FIELDS,
    )
    query_terms = {"TITLE-ABS-KEY": "{combination}"}
    query_terms.update(query_fields)

    logger.debug(query_terms=query_terms)

    search_terms = BOOLEAN_OPERATOR.join(
        f"{field}({value})" for field, value in query_terms.items()
    )

    query_params = _BASE_QUERY_PARAMS.copy()
    query_params["apiKey"] = params.api_key
    query_params["date"] = params.date
    del query_params["start"]

    def _build(combination: str) -> str:
        query_params["query"] = search_terms.format(combination=combination)
        return f"{SEARCH_API_URL}?{urlencode(query_params)}"

    return _build


def build_search_urls(params: SurveyParams) -> Callable[[int], str]:
    query_fields = params.model_dump(
        by_alias=True,
        exclude_unset=True,
        exclude_none=True,
        include=QUERY_FIELDS,
    )
    query_terms = {"TITLE-ABS-KEY": params.combination}
    query_terms.update(query_fields)

    logger.debug(query_terms=query_terms)

    search_terms = BOOLEAN_OPERATOR.join(
        f"{field}({value})" for field, value in query_terms.items()
    )

    query_params = _BASE_QUERY_PARAMS.copy()
    query_params["apiKey"] = params.api_key
    query_params["query"] = search_terms
    query_params["date"] = params.date
    del query_params["count"]

    def _build(start_page: int) -> str:
        query_params["start"] = start_page
        return f"{SEARCH_API_URL}?{urlencode(query_params)}"

    return _build


def build_abstract_urls(api_key: str) -> Callable[[str], str]:
    query_params = {"apiKey": api_key, "field": _FIELDS}

    def _build(abstract_url: str) -> str:
        return f"{abstract_url}?{urlencode(query_params)}"

    return _build
