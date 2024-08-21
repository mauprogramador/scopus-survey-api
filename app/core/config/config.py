from os.path import join
from secrets import token_hex
from tempfile import mkdtemp

from app.core.common.types import Token
from app.utils.logger import Logger
from app.utils.signal_handler import SignalHandler
from app.utils.toml import PyprojectToml

DIRECTORY = mkdtemp()
TOKEN = Token.validate_strings(token_hex(16))

TOKEN_HEADER = "X-Access-Token"
API_KEY_HEADER = "apikey"
KEYWORDS_HEADER = "keywords"

FILENAME = "articles.csv"
HEADERS = {"Content-Disposition": f"attachment; filename={FILENAME}"}
FILE_PATH = join(DIRECTORY, FILENAME)

HANDLER = SignalHandler()
TOML = PyprojectToml()
LOG = Logger(TOML.debug, TOML.logging_file)

LOG.debug(TOML.pyproject)
