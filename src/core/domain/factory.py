from src.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from src.adapters.gateway.scopus_search_api import ScopusSearchAPI
from src.adapters.helpers.http_retry import HTTPRetry
from src.adapters.helpers.scopus_response import ScopusResponse
from src.adapters.helpers.url_builder import URLBuilder
from src.core.common.messages import ABSTRACT_API_ERROR, SEARCH_API_ERROR
from src.core.data.serializers import ScopusAbstract, ScopusSearch
from src.core.data.survey_detail import SurveyDetail
from src.core.use_cases import (
    ArticlesSimilarityFilter,
    ScopusArticlesAggregator,
)


def make_usecase() -> ScopusArticlesAggregator:
    url_builder = URLBuilder()
    survey_detail = SurveyDetail()

    search_http = HTTPRetry(for_search=True)
    search_response = ScopusResponse(ScopusSearch, SEARCH_API_ERROR)

    abstract_http = HTTPRetry(for_search=False)
    abstract_response = ScopusResponse(ScopusAbstract, ABSTRACT_API_ERROR)

    search_api = ScopusSearchAPI(
        search_http, url_builder, search_response, survey_detail
    )

    abstract_api = ScopusAbstractRetrievalAPI(
        abstract_http, url_builder, abstract_response, survey_detail
    )

    similarity_filter = ArticlesSimilarityFilter()

    articles_aggregator = ScopusArticlesAggregator(
        search_api, abstract_api, similarity_filter, survey_detail
    )

    return articles_aggregator
