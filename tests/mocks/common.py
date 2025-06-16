from src.core.data.query_params import SearchParams
from src.framework.fastapi.csrf_token import CSRFToken
from tests.helpers.models import Response
from tests.helpers.utils import scopus_json

API_KEY = "6bd9327547a3cf4c56586324df4b7d92"
KEYWORDS = ["Python", "Machine Learning"]

ANY_DICT = {"any": "any"}

ERROR_CODES = [400, 401, 403, 404, 429, 500]

ERROR_RESPONSES = {code: Response(ANY_DICT, code) for code in ERROR_CODES}
EMPTY_RESPONSE = Response("")
ANY_RESPONSE = Response("any")

__PARAMS = f"?apikey={API_KEY}&keywords={','.join(KEYWORDS)}"
BASE_URL = "/v2/scopus-survey/api"

URL = f"{BASE_URL}/search-articles{__PARAMS}"
TABLE_URL = f"{BASE_URL}/table"

CSV_CONTENT_TYPE = ("content-type", "text/csv; charset=utf-8")
HTML_CONTENT_TYPE = ("content-type", "text/html; charset=utf-8")

# adapters/gateway/scopus_search_api

CSRF_TOKEN, SIGNED_TOKEN = CSRFToken.generate_csrf_tokens()
SEARCH_PARAMS = SearchParams(
    **{"csrf_token": CSRF_TOKEN, "api_key": API_KEY, "keywords": KEYWORDS}
)
VALIDATE_ERROR_RESPONSE = Response(ANY_DICT)
NOT_FOUND = Response(scopus_json(0, []))
