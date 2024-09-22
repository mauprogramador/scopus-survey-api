from app.core.config.config import TOML_ENV
from tests.helpers.models import Response
from tests.helpers.utils import abstract, entry_item, scopus_json
from tests.mocks import unitary as uni
from tests.mocks.common import API_KEY

# adapters/gateway/scopus_search_api

__ABS_RESPONSES = [Response(abstract(letter)) for letter in "abcdefg"]
ONE_PAGE = [*uni.ONE_PAGE, uni.ONE_ABSTRACT]
TWO_PAGES = [*uni.TWO_PAGES, *__ABS_RESPONSES[:4]]
MORE_PAGES = [*uni.MORE_PAGES, *__ABS_RESPONSES]

# adapters/gateway/abstract_retrieval_api

ONE_ROW = [*uni.ONE_PAGE, uni.ONE_ABSTRACT]
TWO_ROWS = [*uni.TWO_PAGES, *__ABS_RESPONSES[:2]]
MORE_ROWS = [*uni.MORE_PAGES, *__ABS_RESPONSES]
EMPTY_RESPONSE = [*uni.ONE_PAGE, Response("")]
DECODING_ERROR_RESPONSE = [*uni.ONE_PAGE, Response("any")]
VALIDATE_ERROR_RESPONSE = [*uni.ONE_PAGE, Response({"any": "any"})]

# framework/dependencies/query_params

NO_PARAMS_URL = f"{TOML_ENV.url}/scopus-searcher/api/search-articles"
API_KEY_URL = f"{NO_PARAMS_URL}?apikey="
NO_KEYWORDS_URL = f"{API_KEY_URL}{API_KEY}"
KEYWORDS_URL = f"{NO_KEYWORDS_URL}&keywords="

# core/usecases/articles_similarity_filter

TWO_SIMILAR_TITLES = [
    Response(scopus_json(2, [entry_item(0)] * 2)),
    Response(abstract("any_title_a")),
    Response(abstract("any_title_b")),
]
MORE_SIMILAR_TITLES = [
    Response(scopus_json(5, [entry_item(0)] * 5)),
    *[Response(abstract(author="aa"))] * 2,
    *[Response(abstract(author="bb"))] * 2,
    Response(abstract()),
]
NO_REPEATED_AUTHORS = [
    Response(scopus_json(2, [entry_item(0)] * 2)),
    Response(abstract(author="aa")),
    Response(abstract(author="bb")),
]
NO_SIMILAR_TITLES = [
    Response(scopus_json(2, [entry_item(0)] * 2)),
    Response(abstract("abc")),
    Response(abstract("def")),
]

# core/usecases/scopus_articles_aggregator

EXACT_DUPLICATES = [
    Response(scopus_json(2, [entry_item(0)] * 2)),
    Response(abstract()),
    Response(abstract()),
]
SAME_TITLE_AND_AUTHORS = [
    Response(scopus_json(2, [entry_item(0)] * 2)),
    Response(abstract(doi="1")),
    Response(abstract(doi="2")),
]
