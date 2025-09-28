from src.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from src.adapters.gateway.scopus_search_api import ScopusSearchAPI
from src.adapters.helpers.http_client import HTTPClient
from src.adapters.helpers.url_builder import URLBuilder
from src.core.data.survey_detail import SurveyDetails
from src.core.use_cases import (
    ArticlesSimilarityFilter,
    ScopusArticlesAggregator,
)
from src.core.use_cases.keyword_combination_finder import (
    KeywordCombinationFinder,
)


def make_combinator() -> KeywordCombinationFinder:
    survey_detail = SurveyDetails()

    url_builder = URLBuilder()
    http_client = HTTPClient()

    search_api = ScopusSearchAPI(http_client, url_builder, survey_detail)

    combinator_finder = KeywordCombinationFinder(
        url_builder, search_api, survey_detail
    )

    return combinator_finder


def make_aggregator() -> ScopusArticlesAggregator:
    survey_detail = SurveyDetails()

    url_builder = URLBuilder()
    search_http_client = HTTPClient()
    abstract_http_client = HTTPClient()

    search_api = ScopusSearchAPI(
        search_http_client, url_builder, survey_detail
    )

    abstract_api = ScopusAbstractRetrievalAPI(
        abstract_http_client, url_builder, survey_detail
    )

    similarity_filter = ArticlesSimilarityFilter()

    articles_aggregator = ScopusArticlesAggregator(
        search_api, abstract_api, similarity_filter, survey_detail
    )

    return articles_aggregator
