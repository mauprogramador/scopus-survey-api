from app.core.config.config import TOML_ENV
from app.core.config.scopus import ABSTRACT_COLUMN, AUTHORS_COLUMN
from app.framework.exceptions import BadGateway, GatewayTimeout
from tests.helpers.data import article, scopus_json, similar_articles, template
from tests.helpers.models import Response
from tests.mocks import unitary as uni
from tests.mocks.common import API_KEY, EMPTY_RESPONSE, ERROR_RESPONSES

# adapters/gateway/scopus_search_api

__EMPTY_RESPONSES = [EMPTY_RESPONSE] * 14
ONE_PAGE = [*uni.ONE_PAGE, *__EMPTY_RESPONSES[:2]]
TWO_PAGES = [*uni.TWO_PAGES, *__EMPTY_RESPONSES[:4]]
MORE_PAGES = [*uni.MORE_PAGES, *__EMPTY_RESPONSES]


# adapters/gateway/scopus_article_page

__TEMPLATE_RESPONSES = [Response(template())] * 7
ONE_ROW = [*uni.ONE_PAGE, __TEMPLATE_RESPONSES[0]]
TWO_ROWS = [*uni.TWO_PAGES, *__TEMPLATE_RESPONSES[:2]]
MORE_ROWS = [*uni.MORE_PAGES, *__TEMPLATE_RESPONSES]
ERROR_RESPONSE = [*uni.ONE_PAGE, *[ERROR_RESPONSES[500]] * 2]
EMPTY_RESPONSE = [*uni.ONE_PAGE, *__EMPTY_RESPONSES[:2]]
EXCEPT_RESPONSE = [*uni.ONE_PAGE, BadGateway("any"), GatewayTimeout("any")]
SECOND_CHANCE_RESPONSE = [
    *uni.ONE_PAGE,
    BadGateway("any"),
    __TEMPLATE_RESPONSES[0],
]

# framework/dependencies/query_params

NO_PARAMS_URL = f"{TOML_ENV.url}/scopus-searcher/api/search-articles"
API_KEY_URL = f"{NO_PARAMS_URL}?apikey="
NO_KEYWORDS_URL = f"{API_KEY_URL}{API_KEY}"
KEYWORDS_URL = f"{NO_KEYWORDS_URL}&keywords="


# core/usecases/articles_similarity_filter

TWO_SIMILAR_TITLES = similar_articles(True, {"a": 2})
MORE_SIMILAR_TITLES = similar_articles(True, {"a": 2, "b": 2, "c": 1})
NO_REPEATED_AUTHORS = similar_articles(False, {"a": 1, "b": 1})
NO_SIMILAR_TITLES = similar_articles((False, True), {"a": 2})


# core/usecases/scopus_articles_aggregator

__EXACT_DUPLICATE_RESPONSE = Response(scopus_json(2, [article()] * 2))
EXACT_DUPLICATES = [__EXACT_DUPLICATE_RESPONSE, *__EMPTY_RESPONSES[:2]]
INSERTED_COLUMNS = [AUTHORS_COLUMN, ABSTRACT_COLUMN]
__SAME_RESPONSE = Response(scopus_json(2, [article(doi=doi) for doi in "12"]))
SAME_TITLE_AND_AUTHORS = [__SAME_RESPONSE, *__EMPTY_RESPONSES[:4]]
