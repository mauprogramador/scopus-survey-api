from datetime import datetime

DATE_RANGE = f"{datetime.now().year - 3}-{datetime.now().year}"
BOOLEAN_OPERATOR = " AND "
PAGINATION_SUFFIX = "&start="
NULL = "null"

TOTAL_RESULTS_FIELD = "opensearch:totalResults"
ITEMS_PER_PAGE_FIELD = "opensearch:itemsPerPage"
SEARCH_RESULTS_FIELD = "search-results"

RESET_HEADER = "X-RateLimit-Reset"
STATUS_HEADER = "X-ELS-Status"
QUOTA_EXCEEDED = "QUOTA_EXCEEDED"

QUOTA_LOG = (
    "Your APIKey has exceeded the request quota. Please try again on {}"
)
LINK_LOG = (
    "For further information visit "
    "https://dev.elsevier.com/api_key_settings.html"
)

AUTHORS_SELECTOR = "#authorlist .list-inline li .previewTxt"
ABSTRACT_SELECTOR = "#abstractSection p"

SCOPUS_ID_COLUMN = "dc:identifier"
URL_COLUMN = "prism:url"
LINK_COLUMN = "@_fa"
AUTHORS_COLUMN = "Authors"
ABSTRACT_COLUMN = "Abstract"
TEMPLATE_COLUMN = "Template"
TITLE_COLUMN = "Title"

API_URL = (
    "https://api.elsevier.com/content/search/scopus"
    "?query=TITLE-ABS-KEY({query})&field={fields}&date={date}"
    "&suppressNavLinks=true"
)
ARTICLE_PAGE_URL = (
    "https://www.scopus.com/inward/record.uri"
    "?partnerID=HzOxMe3b&scp={scopus_id}&origin=inward"
)
FIELDS = (
    "prism:coverDate,prism:url,prism:publicationName,"
    "citedby-count,prism:volume,dc:title,prism:doi,dc:identifier"
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

COLUMNS_MAPPING = {
    "prism:publicationName": "Publication Name",
    "prism:coverDate": "Date",
    "dc:identifier": "Scopus Id",
    "prism:url": "URL",
    "dc:title": "Title",
    "prism:volume": "Volume",
    "prism:doi": "DOI",
    "citedby-count": "Citations",
}


def get_search_headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
        "X-ELS-APIKey": api_key,
    }


SCRAPING_HEADERS = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Referer": "https://www.scopus.com/",
    "Connection": "keep-alive",
    "Content-Type": "text/plain",
    "Origin": "https://www.scopus.com",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9"
        ",image/avif,image/webp,image/apng,*/*;q=0.8,application/"
        "signed-exchange;v=b3;q=0.7"
    ),
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ),
}
