from datetime import datetime

DATE_RANGE = f"{datetime.now().year - 3}-{datetime.now().year}"
BOOLEAN_OPERATOR = " AND "
NULL = "null"

RESET_HEADER = "X-RateLimit-Reset"
STATUS_HEADER = "X-ELS-Status"
QUOTA_EXCEEDED = "QUOTA_EXCEEDED - Quota Exceeded"

AUTHORS_COLUMN = "Authors"
TITLE_COLUMN = "Title"

QUOTA_WARNING = (
    "Your APIKey has exceeded the request quota. Please try again on {}"
)
FURTHER_INFO_LINK = (
    "For further information visit "
    "https://dev.elsevier.com/api_key_settings.html"
)

SEARCH_API_URL = (
    "https://api.elsevier.com/content/search/scopus"
    "?query=TITLE-ABS-KEY({query})&field=dc:identifier&date={date}"
    "&suppressNavLinks=true"
)
PAGINATION_URL = "{search_url}&start={page}"
ABSTRACT_API_URL = "{abstract_url}?field={fields}"

FIELDS = (
    "dc:identifier,eid,dc:title,dc:description,prism:publicationName,citedby"
    "-count,prism:volume,prism:coverDate,prism:doi,dc:creator,authors"
)

API_ERRORS = {
    400: "Invalid request. Invalid information submitted",
    401: "User cannot be authenticated due to missing/invalid credentials",
    403: "User cannot be authenticated or entitlements cannot be validated",
    429: (
        "The requester has exceeded the quota "
        "limits associated with their APIKey"
    ),
    500: "Scopus API internal processing error",
}


def get_scopus_headers(api_key: str) -> dict[str, str]:
    return {
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.scopus.com/",
        "Origin": "https://www.scopus.com",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Connection": "keep-alive",
        "X-ELS-APIKey": api_key,
    }
