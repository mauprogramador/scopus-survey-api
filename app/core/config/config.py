from secrets import token_hex

from app.core.common.types import Token
from app.utils.logger import ApplicationLogger
from app.utils.signal_handler import ShutdownSignalHandler
from app.utils.toml_env import TomlEnvConfig


TOKEN = Token.validate_strings(token_hex(nbytes=16))

TOKEN_HEADER = "X-Access-Token"
CSV_HEADER = "X-CSV-Filename"
USER_API_KEY_HEADER = "X-User-API-Key"

API_KEY_QUERY = "apikey"
KEYWORDS_QUERY = "keywords"

DIRECTORY = "csv"
FILE = "articles.csv"

HANDLER = ShutdownSignalHandler()
TOML_ENV = TomlEnvConfig()
LOG = ApplicationLogger(**TOML_ENV.logger_config)

LOG.debug(TOML_ENV.pyproject)
