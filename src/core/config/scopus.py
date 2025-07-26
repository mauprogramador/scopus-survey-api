from datetime import datetime
from http import HTTPStatus

CURRENT_YEAR = datetime.now().year
LAST_THREE_YEARS = CURRENT_YEAR - 3
LAST_DECADE = CURRENT_YEAR - 10

BOOLEAN_OPERATOR = " AND "
NULL = "null"

NO_RESULTS = "NO_SEARCH_RESULTS"
EMPTY_RESULT = "Result set was empty"

SEARCH_API_URL = "https://api.elsevier.com/content/search/scopus"
ARTICLE_PAGE_URL = "https://www.scopus.com/inward/record.uri"

SCOPUS_DOCS = "https://dev.elsevier.com/documentation"
FOOTNOTE = (
    "# The data was retrieved from Scopus APIs on {date} via "
    "http://api.elsevier.com and http://www.scopus.com."
)

QUERY_FIELDS = {
    "doctype",
    "pubstage",
    "language",
    "open_access",
    "source_type",
    "subject_area",
    "pages",
}

SEARCH_FIELDS = (
    "dc:identifier",
    "eid",
    "dc:title",
    "dc:description",
    "prism:publicationName",
    "cited",
    "by-count",
    "prism:volume",
    "prism:coverDate",
    "prism:doi",
    "dc:creator",
    "authors",
)

SCOPUS_HEADERS = {
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.scopus.com/",
    "Origin": "https://www.scopus.com",
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
}

SCOPUS_ERRORS = {
    HTTPStatus.BAD_REQUEST: "Invalid Request: invalid information submitted",
    HTTPStatus.UNAUTHORIZED: (
        "Authentication Error: user cannot be authenticated due to missing"
        "/invalid credentials"
    ),
    HTTPStatus.FORBIDDEN: (
        "Authorization/Entitlements Error: User cannot be authenticated or "
        "entitlements cannot be validated"
    ),
    HTTPStatus.NOT_FOUND: (
        "Resource Not Found Error: This is an error that occurs when the "
        "requested resource cannot be found"
    ),
    HTTPStatus.TOO_MANY_REQUESTS: (
        "Quota Exceeded: the requester has exceeded the quota limits "
        "associated with their API Key"
    ),
    HTTPStatus.INTERNAL_SERVER_ERROR: (
        "Generic Error: Scopus API back-end processing errors"
    ),
}
