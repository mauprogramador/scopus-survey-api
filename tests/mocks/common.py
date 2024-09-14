from pandas import DataFrame

from app.core.common.types import SearchParams
from app.core.config.config import TOML_ENV
from app.core.config.scopus import ABSTRACT_COLUMN, AUTHORS_COLUMN, URL_COLUMN
from tests.helpers.data import article, scopus_json
from tests.helpers.models import Response

API_KEY = "6bd9327547a3cf4c56586324df4b7d92"
KEYWORDS = ["Python", "Machine Learning"]
ANY_DICT = {"any": "any"}

INVALID_LONG_VALUE = "est esse ip sumo lor cupidatat dolore fug at"
INVALID_PATTERN_VALUE = "b7@56!b$d5cf@3f!sH%3P3*d2db$5c@e"

SCOPUS_API_JSON = scopus_json(156, [article()])
ERROR_CODES = [400, 401, 403, 404, 429, 500]

ERROR_RESPONSES = {code: Response(ANY_DICT, code) for code in ERROR_CODES}
EMPTY_RESPONSE = Response("")
ANY_RESPONSE = Response("any")

__PARAMS = f"?apikey={API_KEY}&keywords={','.join(KEYWORDS)}"
BASE_URL = f"{TOML_ENV.url}/scopus-searcher/api"

URL = f"{BASE_URL}/search-articles{__PARAMS}"
TABLE_URL = f"{BASE_URL}/table"

CSV_CONTENT_TYPE = ("content-type", "text/csv; charset=utf-8")
HTML_CONTENT_TYPE = ("content-type", "text/html; charset=utf-8")


# adapters/gateway/scopus_search_api

SEARCH_PARAMS = SearchParams(api_key=API_KEY, keywords=KEYWORDS)
VALIDATE_ERROR_RESPONSE = Response(ANY_DICT)
NOT_FOUND = Response(scopus_json(0, []))


# core/usecases/scopus_articles_aggregator

SCRAPE_COLUMNS = [URL_COLUMN, AUTHORS_COLUMN, ABSTRACT_COLUMN]


# adapters/presenters/template_context

CSV_DATA = DataFrame({"any": ["any", "any"]})
