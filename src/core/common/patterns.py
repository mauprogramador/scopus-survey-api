# e.g. 127.0.0.1, 0.0.0.0
HOST_PATTERN = r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$"

# e.g. \033[35;1m, \033[m
ANSI_ESCAPE_PATTERN = r"\x1b\[[0-9\;]*m"

# e.g. 6bd9327547a3cf4c56586324df4b7d92
API_KEY_PATTERN = r"^[a-zA-Z0-9]{32}$"

# e.g. Python, Multi-task
KEYWORD_PATTERN = r"^[a-zA-Z0-9\-\_ ]{2,50}$"

# e.g. 989a5e2a50389ae6a5faf4c271d8bfb30cbbd88c
TOKEN_PATTERN = r"^[a-zA-Z0-9]{40}$"

# e.g. /v2/scopus-survey/api
API_ROUTES_PATTERN = r"^\/v2\/scopus-survey\/api\/(combination|survey|csv)"

# e.g. english, portuguese
LANGUAGE_PATTERN = r"^[a-z\-\' ]{2,}$"

# e.g. Python AND Multi-task
COMBINATION_PATTERN = r"^[a-zA-Z0-9\-\_ ]{2,150}$"
