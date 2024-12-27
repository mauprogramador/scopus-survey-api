from app.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from app.adapters.gateway.scopus_search_api import ScopusSearchAPI
from app.adapters.helpers.http_retry import HTTPRetry
from app.adapters.helpers.url_builder import URLBuilder
from app.core.usecases import (
    ArticlesSimilarityFilter,
    ScopusArticlesAggregator,
)


def make_usecase() -> ScopusArticlesAggregator:
    url_builder = URLBuilder()

    scopus_http = HTTPRetry(for_search=True)
    articles_http = HTTPRetry(for_search=False)

    search_api = ScopusSearchAPI(scopus_http, url_builder)
    abstract_api = ScopusAbstractRetrievalAPI(articles_http, url_builder)

    similarity_filter = ArticlesSimilarityFilter()

    articles_aggregator = ScopusArticlesAggregator(
        search_api, abstract_api, similarity_filter
    )

    return articles_aggregator
