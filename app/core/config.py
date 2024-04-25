from datetime import datetime
from re import compile as compile_pattern
from secrets import token_hex
from tempfile import mkdtemp

from app.utils.toml import PyprojectToml

DIRECTORY = mkdtemp()
CURRENT_YEAR = datetime.now().year
TOKEN = token_hex(16)
TOML = PyprojectToml()

# Match: no spaces, only letters and numbers; length of exactly 32.
API_KEY_PATTERN = r'^[a-zA-Z0-9]{32}$'

# Match: letters, numbers, spaces and underscores; length between 2 and 120.
KEYWORD_PATTERN = compile_pattern(r'^[a-zA-Z0-9_ ]{2,120}$')

# Match: two or more consecutive spaces.
SPACES_PATTERN = r' {2,}'

# Match: no spaces, only letters and numbers; length of exactly 32.
TOKEN_PATTERN = r'^[a-zA-Z0-9]{32}$'
