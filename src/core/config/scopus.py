from datetime import datetime


CURRENT_YEAR = datetime.now().year
# Last 3 years: considering rapidly evolving fields of study.
LAST_THREE_YEARS = CURRENT_YEAR - 3
# Last 15 years: considering slowly evolving fields of study (with leeway).
MAX_RECENT_PUBLICATIONS = CURRENT_YEAR - 15

BOOLEAN_OPERATOR = " AND "
NULL = "null"

# Scopus Search API response standard
# https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl
MAX_ITEMS_PER_PAGE = 25

# Scopus Search API quota standard
# https://dev.elsevier.com/api_key_settings.html
MAX_SEARCH_QUOTA = 20000

NO_RESULTS = "NO_SEARCH_RESULTS"
EMPTY_RESULT = "Result set was empty"

QUOTA_ERROR_CODE = "QUOTA_EXCEEDED"
RATE_LIMIT_ERROR_CODE = "RATE_LIMIT_EXCEEDED"

SEARCH_API_URL = "https://api.elsevier.com/content/search/scopus"
ARTICLE_PAGE_URL = "https://www.scopus.com/inward/record.uri"

SCOPUS_DOCS = "https://dev.elsevier.com/documentation"
DATA_SOURCE_NOTE = (
    "data retrieved from Scopus APIs on {date} via "
    "http://api.elsevier.com and http://www.scopus.com."
)

QUERY_FIELDS = {
    "doctype",
    "pubstage",
    "language",
    "open_access",
    "source_type",
    "subject_area",
    "page_range",
}

SEARCH_FIELDS = (
    "dc:identifier",
    "eid",
    "dc:title",
    "dc:description",
    "prism:publicationName",
    "citedby-count",
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
