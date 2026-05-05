from src.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from src.adapters.gateway.scopus_search_api import ScopusSearchAPI
from src.adapters.helpers.http_client import HTTPClient
from src.adapters.helpers.url_builder import URLBuilder
from src.core.data.quota_results_handler import QuotaResultsHandler
from src.core.data.survey_details import SurveyDetails
from src.core.use_cases import (
    ArticlesSimilarityFilter,
    ScopusArticlesAggregator,
)
from src.core.use_cases.keyword_combination_finder import (
    KeywordCombinationFinder,
)


def make_combinator() -> KeywordCombinationFinder:
    survey_details = SurveyDetails()

    url_builder = URLBuilder()
    http_client = HTTPClient()

    search_api = ScopusSearchAPI(
        http_client, url_builder, survey_details, None
    )

    combinator_finder = KeywordCombinationFinder(
        url_builder, search_api, survey_details
    )

    return combinator_finder


def make_aggregator() -> ScopusArticlesAggregator:
    survey_details = SurveyDetails()
    state = QuotaResultsHandler()

    url_builder = URLBuilder()
    http_client = HTTPClient()

    search_api = ScopusSearchAPI(
        http_client, url_builder, survey_details, state
    )

    abstract_api = ScopusAbstractRetrievalAPI(
        http_client, url_builder, survey_details, state
    )

    similarity_filter = ArticlesSimilarityFilter()

    articles_aggregator = ScopusArticlesAggregator(
        search_api, abstract_api, similarity_filter, survey_details
    )

    return articles_aggregator
