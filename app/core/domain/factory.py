from app.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from app.adapters.helpers.scopus_response import ScopusResponse
from app.adapters.gateway.scopus_search_api import ScopusSearchAPI
from app.adapters.helpers.http_retry import HTTPRetry
from app.adapters.helpers.url_builder import URLBuilder
from app.core.common.messages import ABSTRACT_API_ERROR, SEARCH_API_ERROR
from app.core.data.serializers import ScopusAbstract, ScopusSearch
from app.core.use_cases import (
    ArticlesSimilarityFilter,
    ScopusArticlesAggregator,
)


def make_usecase() -> ScopusArticlesAggregator:
    url_builder = URLBuilder()

    search_http = HTTPRetry(for_search=True)
    search_response = ScopusResponse(ScopusSearch, SEARCH_API_ERROR)

    abstract_http = HTTPRetry(for_search=False)
    abstract_response = ScopusResponse(ScopusAbstract, ABSTRACT_API_ERROR)

    search_api = ScopusSearchAPI(search_http, url_builder, search_response)
    abstract_api = ScopusAbstractRetrievalAPI(
        abstract_http, url_builder, abstract_response
    )

    similarity_filter = ArticlesSimilarityFilter()

    articles_aggregator = ScopusArticlesAggregator(
        search_api, abstract_api, similarity_filter
    )

    return articles_aggregator
