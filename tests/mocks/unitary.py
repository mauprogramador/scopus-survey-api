from pandas import DataFrame

from app.core.config.scopus import NULL
from tests.helpers.data import (
    article,
    article_page_subsets,
    no_link_article,
    pagination,
    scrap_subset,
    similar_data,
    template,
)
from tests.helpers.models import Request, Response, HeadersResponse

# adapters/gateway/scopus_search_api

ARTICLES = [article(f"any{index}") for index in range(7)]
NO_LINK_ARTICLES = [no_link_article(f"any{index}") for index in range(7)]
ONE_PAGE = pagination(ARTICLES[:1])
TWO_PAGES = pagination(ARTICLES[:2])
MORE_PAGES = pagination(ARTICLES)
EXCEEDED_RESPONSE = HeadersResponse()


# adapters/gateway/scopus_article_page

ANY_PAGES = [Response("any")] * 7
DF_IN, DF_OUT = article_page_subsets()
ONE_ROW = DF_IN.iloc[0:1]
TWO_ROWS = DF_IN.iloc[0:2]
DF_INVALID = DataFrame({"any": ["any", "any"]})


# adapters/helpers/http_retry_helper

JSONPLACEHOLDER = "https://jsonplaceholder.typicode.com/users/1"
HEADERS = {"Content-Type": "application/json"}


# adapters/presenters/template_context

EMPTY_REQUEST = Request()


# core/usecases/articles_page_scraper

SUBSET_TEMPLATE = scrap_subset(template())
SUBSET_NULL = scrap_subset(NULL)
SUBSET_MULTIPLE = scrap_subset([template(), NULL, template(), NULL])
SCRAP_DATA = ["any", "any1 A., any2 B.", "any abstract"]


# core/usecases/articles_similarity_filter

TWO_SIMILAR_TITLES = similar_data(True, {"a": 2})
MORE_SIMILAR_TITLES = similar_data(True, {"a": 2, "b": 2, "c": 1})
NO_REPEATED_AUTHORS = similar_data(False, {"a": 1, "b": 1})
NO_SIMILAR_TITLES = similar_data(False, {"a": 2})


# core/usecases/scopus_articles_aggregator

ONE_ARTICLE = DataFrame([no_link_article()])
MORE_ARTICLES = DataFrame([no_link_article(letter) for letter in "abcdefg"])
EXACT_DUPLICATES = DataFrame([no_link_article()] * 2)
SAME_TITLE_AND_AUTHORS = DataFrame([no_link_article(doi=doi) for doi in "12"])
