from app.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from app.adapters.gateway.scopus_search_api import ScopusSearchAPI
from app.adapters.helpers.http_retry_helper import HTTPRetryHelper
from app.adapters.helpers.url_builder_helper import URLBuilderHelper
from app.core.usecases import (
    ArticlesSimilarityFilter,
    ScopusArticlesAggregator,
)


def make_usecase() -> ScopusArticlesAggregator:
    url_builder = URLBuilderHelper()

    scopus_http_helper = HTTPRetryHelper(for_search=True)
    articles_http_helper = HTTPRetryHelper(for_search=False)

    search_api = ScopusSearchAPI(scopus_http_helper, url_builder)
    abstract_api = ScopusAbstractRetrievalAPI(
        articles_http_helper, url_builder
    )

    similarity_filter = ArticlesSimilarityFilter()

    articles_aggregator = ScopusArticlesAggregator(
        search_api, abstract_api, similarity_filter
    )

    return articles_aggregator
