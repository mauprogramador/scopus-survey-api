from re import compile as compile_pattern

# Match: no spaces, only letters and numbers; length of exactly 32.
API_KEY_PATTERN = r"^[a-zA-Z0-9]{32}$"

# Match: letters, numbers, spaces and underscores; length between 2 and 50.
KEYWORD_PATTERN = compile_pattern(r"^(?!\s*$)[a-zA-Z0-9_ ]{2,50}$")

# Match: two or more consecutive spaces.
SPACES_PATTERN = r" {2,}"

# Match: no spaces, only letters and numbers; length of exactly 32.
TOKEN_PATTERN = r"^[a-zA-Z0-9]{32}$"
