from datetime import datetime
from http import HTTPMethod, HTTPStatus
from secrets import token_hex
from time import time
from unittest.mock import Mock

from fastapi import Request
from fastapi.datastructures import URL, Headers, QueryParams

from src.core.common.types import LogParams
from src.core.config.config import FILE, MAX_AGE
from src.core.config.scopus import (
    EMPTY_RESULT,
    QUOTA_ERROR_CODE,
    RATE_LIMIT_ERROR_CODE,
)
from src.core.data.enums import Button, Lang
from src.core.data.serializers import ScopusHeaders
from src.framework.fastapi.csrf_token import CSRFToken
from src.utils.logging import Logging


# HTTP Status code

HTTP_200 = HTTPStatus.OK
HTTP_400 = HTTPStatus.BAD_REQUEST
HTTP_401 = HTTPStatus.UNAUTHORIZED
HTTP_422 = HTTPStatus.UNPROCESSABLE_ENTITY
HTTP_429 = HTTPStatus.TOO_MANY_REQUESTS
HTTP_404 = HTTPStatus.NOT_FOUND
HTTP_500 = HTTPStatus.INTERNAL_SERVER_ERROR
HTTP_502 = HTTPStatus.BAD_GATEWAY
HTTP_503 = HTTPStatus.SERVICE_UNAVAILABLE
HTTP_504 = HTTPStatus.GATEWAY_TIMEOUT

# Client params

API_KEY = token_hex(16)
CSRF_TOKEN, SIGNED_TOKEN = CSRFToken.generate_csrf_tokens()
KEYWORDS = ["Python", "AI", "Automation", "Web"]
CSV_FILE_NAME = f"{API_KEY}_{FILE}"

URL_WEB = f"/web/{Lang.EN_US}/survey-bibliographies"
URL_COMBINATION = "/api/combination"
URL_SEARCH = "/api/survey"
URL_CSV = "/api/csv"

CSV_PARAMS = {
    "apiKey": API_KEY,
    "button": Button.PREVIOUS.value,
}
COMBINATION_PARAMS = {
    "apiKey": API_KEY,
    "keywords": KEYWORDS[:2],
    "button": Button.COMBINATION.value,
}
SEARCH_PARAMS = {
    "apiKey": API_KEY,
    "keywords": KEYWORDS[:2],
    "combination": KEYWORDS[0],
    "button": Button.SURVEY.value,
}

CSV_MEDIA = "text/csv"
HTML_MEDIA = "text/html"
CSV_CONTENT_TYPE = f"{CSV_MEDIA}; charset=utf-8"
HTML_CONTENT_TYPE = f"{HTML_MEDIA}; charset=utf-8"
JSON_CONTENT_TYPE = "application/json; charset=utf-8"

# Scopus APIs responses

ABSTRACT_URL = "https://api.elsevier.com/content/abstract/scopus_id/0123456789"
SCOPUS_ID = "SCOPUS_ID:0123456789"
RESET = int(time()) + MAX_AGE
RESET_DATETIME = datetime.fromtimestamp(RESET).strftime("%Y-%m-%d %H:%M:%S")
RAW_HEADERS_OK = {
    "X-RateLimit-Limit": "20000",
    "X-RateLimit-Remaining": "20000",
    "X-RateLimit-Reset": str(RESET),
    "X-ELS-Status": "OK",
}
RAW_HEADERS_ONE_QUOTA = {
    "X-RateLimit-Limit": "20000",
    "X-RateLimit-Remaining": "1",
    "X-RateLimit-Reset": str(RESET),
    "X-ELS-Status": "OK",
}
RAW_HEADERS_NO_QUOTA = {
    "X-RateLimit-Limit": "20000",
    "X-RateLimit-Remaining": "0",
    "X-RateLimit-Reset": str(RESET),
    "X-ELS-Status": QUOTA_ERROR_CODE,
}
RAW_ENTRY = {
    "@_fa": "true",
    "prism:url": ABSTRACT_URL,
    "dc:identifier": SCOPUS_ID,
}
RAW_SEARCH_OK = {
    "search-results": {
        "opensearch:totalResults": "1",
        "opensearch:itemsPerPage": "1",
        "entry": [RAW_ENTRY],
    }
}
RAW_SEARCH_NOT_FOUND = {
    "search-results": {
        "opensearch:totalResults": "0",
        "opensearch:itemsPerPage": "0",
        "entry": [{"@_fa": "true", "error": EMPTY_RESULT}],
    }
}
RAW_ABSTRACT_OK = {
    "abstracts-retrieval-response": {
        "coredata": {
            "dc:identifier": SCOPUS_ID,
            "dc:title": "any_title",
            "dc:creator": {"author": [{"ce:indexed-name": "any_author"}]},
        }
    }
}
RAW_ABSTRACT_AUTHORS = {
    "abstracts-retrieval-response": {
        "coredata": {
            "dc:identifier": SCOPUS_ID,
            "dc:title": "any_title",
        },
        "authors": {
            "author": [
                {"ce:indexed-name": "any_author_1"},
                {"ce:indexed-name": "any_author_2"},
            ]
        },
    }
}
RAW_ABSTRACT_FULL = {
    "abstracts-retrieval-response": {
        "coredata": {
            "dc:identifier": SCOPUS_ID,
            "dc:title": "any_title",
            "prism:publicationName": "any_publication_name",
            "dc:description": "any_abstract",
            "prism:coverDate": "any_date",
            "eid": "any_eid",
            "prism:doi": "any_doi",
            "prism:volume": "any_volume",
            "citedby-count": "any_citations",
            "dc:creator": {"author": [{"ce:indexed-name": "any_author"}]},
        }
    }
}
RAW_SERVICE_ERROR_QUOTA = {
    "service-error": {"status": {"statusCode": QUOTA_ERROR_CODE}}
}
RAW_ERROR_RESPONSE_RATE_LIMIT = {
    "error-response": {"error-code": RATE_LIMIT_ERROR_CODE}
}
LOG_QUOTA = (ScopusHeaders(**RAW_HEADERS_OK), HTTPStatus.OK.value)
LOG_ONE_QUOTA = (ScopusHeaders(**RAW_HEADERS_ONE_QUOTA), HTTPStatus.OK.value)
LOG_NO_QUOTA = (ScopusHeaders(**RAW_HEADERS_NO_QUOTA), HTTPStatus.OK.value)

# Models params

ALIAS_CSV_PARAMS = {"api_key": API_KEY, "button": Button.PREVIOUS.value}
ALIAS_COMBINATION_PARAMS = {
    "api_key": API_KEY,
    "keywords": KEYWORDS,
    "button": Button.COMBINATION.value,
}
ALIAS_COMBINATION_PARAMS_FULL = {
    "api_key": API_KEY,
    "start_year": "2020",
    "end_year": "2021",
    "doctype": "ar",
    "pubstage": "final",
    "language": "english",
    "open_access": "0",
    "source_type": "j",
    "subject_area": "COMP",
    "pages": "short",
    "keywords": KEYWORDS,
    "button": Button.COMBINATION.value,
}
ALIAS_SEARCH_PARAMS = {
    "api_key": API_KEY,
    "keywords": KEYWORDS,
    "combination": "Python AND AI",
    "button": Button.SURVEY.value,
}
ALIAS_SEARCH_PARAMS_FULL = {
    "api_key": API_KEY,
    "start_year": "2020",
    "end_year": "2021",
    "doctype": "ar",
    "pubstage": "final",
    "language": "english",
    "open_access": "0",
    "source_type": "j",
    "subject_area": "COMP",
    "pages": "short",
    "keywords": KEYWORDS,
    "combination": "Python AND AI",
    "ratio": "25",
    "button": Button.SURVEY.value,
}

# Mocks

SKIPROWS = (0, 1, 2, 3)  # CSV metadata rows
REQUEST = Mock(
    spec=Request,
    url=URL("http://any.com/mock"),
    method=HTTPMethod.GET,
    headers=Headers({"any": "any"}),
    cookies={},
    session={},
    query={},
    query_params=QueryParams({}),
    client=None,
)


class LOG(Logging): ...


LOG_MOCK = LOG(Mock(LogParams))
