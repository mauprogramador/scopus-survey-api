# e.g. 127.0.0.1, 0.0.0.0
HOST_PATTERN = r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$"

# e.g. \033[35;1m, \033[m
ANSI_ESCAPE_PATTERN = r"\x1b\[[0-9\;]*m"

# e.g. SCOPUS_ID:0123456789
SCOPUS_ID_PATTERN = r"^SCOPUS_ID\:[0-9]{10,}$"

# e.g. http://api.elsevier.com/content/abstract/scopus_id/0123456789
ABSTRACT_URL_PATTERN = (
    r"^https\:\/\/api\.elsevier\.com\/content\/abstract"
    r"\/scopus_id\/[0-9]{10,}$"
)

# e.g. 6bd9327547a3cf4c56586324df4b7d92  - Random Hash
API_KEY_PATTERN = r"^[a-zA-Z0-9]{32}$"

# e.g. apiKey=6bd9327547a3cf4c56586324df4b7d92  - Random Hash
API_KEY_LOG_PATTERN = r"apiKey\=[a-zA-Z0-9]{32}"

# e.g. Python, Multi-task
KEYWORD_PATTERN = r"^[a-zA-Z0-9\{\}\?\"\*\-\_ ]{2,50}$"

# e.g. 989a5e2a50389ae6a5faf4c271d8bfb30cbbd88c  - Random Hash
TOKEN_PATTERN = r"^[a-zA-Z0-9]{40}$"

# e.g. /v2/scopus-survey/api
API_ROUTES_PATTERN = r"^\/v2\/scopus-survey\/api\/(combination|survey|csv)"

# e.g. english, portuguese
LANGUAGE_PATTERN = r"^[a-z\-\' ]{3,30}$"

# e.g. Python AND Multi-task
COMBINATION_PATTERN = r"^[a-zA-Z0-9\{\}\?\"\*\-\_ ]{2,215}$"
