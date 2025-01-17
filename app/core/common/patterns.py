# e.g. 127.0.0.1, 0.0.0.0
HOST_PATTERN = r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$"

# e.g. \033[35;1m, \033[m
ANSI_ESCAPE_PATTERN = r"\x1b\[[0-9\;]*m"

# e.g. 6bd9327547a3cf4c56586324df4b7d92
API_KEY_PATTERN = r"^[a-zA-Z0-9]{32}$"

# e.g. Python, Multi-task
KEYWORD_PATTERN = r"^[a-zA-Z0-9\-_ ]{2,50}$"

# e.g. 313000b9c7b0adf0b1ed24c7c890c551
TOKEN_PATTERN = r"^[a-zA-Z0-9]{32}$"

# e.g. /v2/scopus-survey/api/en-US/search-articles
LANG_ROUTES_PATTERN = (
    r"^\/v2\/scopus-survey\/api\/[a-z]{2}-[A-Z]{2}"
    r"\/(search-articles|articles-table)$"
)

# e.g. /v2/scopus-survey/api/survey
SURVEY_ROUTE_PATTERN = r"^\/v2\/scopus-survey\/api\/survey"

# e.g. /v2/scopus-survey/api/csv
CSV_ROUTE_PATTERN = r"^\/v2\/scopus-survey\/api\/csv"

# e.g. /v2/scopus-survey/api/en-US/search-articles
SEARCH_ROUTE_PATTERN = (
    r"^\/v2\/scopus-survey\/api\/[a-z]{2}-[A-Z]{2}\/search-articles"
)

# e.g. /v2/scopus-survey/api/en-US/articles-table
TABLE_ROUTE_PATTERN = (
    r"^\/v2\/scopus-survey\/api\/[a-z]{2}-[A-Z]{2}\/articles-table"
)
