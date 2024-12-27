from re import compile as compile_pattern

# Match: no spaces, only letters and numbers; length of exactly 32.
API_KEY_PATTERN = r"^[a-zA-Z0-9]{32}$"

# Match: letters, numbers, spaces and underscores; length between 2 and 50.
KEYWORD_PATTERN = compile_pattern(r"^[a-zA-Z0-9\-_ ]{2,50}$")

# Match: no spaces, only letters and numbers; length of exactly 32.
TOKEN_PATTERN = r"^[a-zA-Z0-9]{32}$"

# Match: supported languages routes
LANG_ROUTES = compile_pattern(
    r"^\/scopus-survey\/api\/[a-zA-Z]+\/(search-articles|articles-table)$"
)

# Match: survey route
SURVEY_ROUTE = compile_pattern(r"^\/scopus-survey\/api\/survey")
