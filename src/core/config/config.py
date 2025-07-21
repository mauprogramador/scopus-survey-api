from pathlib import Path
from secrets import token_hex, token_urlsafe

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.config.env_csrf import EnvConfig
from src.utils.logging import Logging

APP = "src.framework.fastapi.main:app"
PREFIX = "/v2/scopus-survey"

DIRECTORY = Path("csv")
FILE = "articles.csv"

TOKEN = token_hex(nbytes=20)
SECRET_KEY = token_urlsafe(nbytes=20)
SALT = "scopus-survey-csrf-token"

ENV = EnvConfig()
LOG = Logging(ENV.log_params)

LIMITER = Limiter(key_func=get_remote_address)
LIMIT = "60/2seconds"

MAX_AGE = 3600  # 1 hour
SHUTDOWN_TIMEOUT = 5

HEADERS = [
    (
        "Content-Security-Policy",
        (
            "default-src 'self'; base-uri 'self'; connect-src 'self'; "
            "child-src 'none'; frame-src 'none'; frame-ancestors 'none'; "
            "form-action 'self'; img-src 'self' data: https://fastapi."
            "tiangolo.com/img/favicon.png; style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui."
            "css; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr"
            ".net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"
        ),
    ),
    ("Cross-Origin-Opener-Policy", "same-origin"),
    ("Referrer-Policy", "strict-origin-when-cross-origin"),
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("X-XSS-Protection", "1; mode=block"),
]
