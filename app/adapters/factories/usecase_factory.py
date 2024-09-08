from app.adapters.gateway.scopus_articles_page import ScopusArticlesPage
from app.adapters.gateway.scopus_search_api import ScopusSearchAPI
from app.adapters.helpers.http_retry_helper import HTTPRetryHelper
from app.adapters.helpers.url_builder_helper import URLBuilderHelper
from app.core.usecases import (
    ArticlesPageScraper,
    ArticlesSimilarityFilter,
    ScopusArticlesAggregator,
)


def make_usecase() -> ScopusArticlesAggregator:
    url_builder = URLBuilderHelper()

    scopus_http_helper = HTTPRetryHelper(for_scopus=True)
    articles_http_helper = HTTPRetryHelper(for_scopus=False)

    search_api = ScopusSearchAPI(scopus_http_helper, url_builder)
    articles_page = ScopusArticlesPage(articles_http_helper, url_builder)

    articles_scraper = ArticlesPageScraper(articles_page)
    similarity_filter = ArticlesSimilarityFilter()

    articles_aggregator = ScopusArticlesAggregator(
        search_api, articles_scraper, similarity_filter
    )

    return articles_aggregator
