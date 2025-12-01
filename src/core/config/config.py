from contextvars import ContextVar
from pathlib import Path
from secrets import token_hex, token_urlsafe

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.config.env import EnvConfig
from src.utils.logging import Logging

APP = "src.framework.fastapi.main:app"
PREFIX = "/v2/scopus-survey"
TRACE_ID_CTX: ContextVar[str] = ContextVar("trace_id")

DIRECTORY = Path("csv")
FILE = "docs.csv"

TOKEN = token_hex(nbytes=20)
SECRET_KEY = token_urlsafe(nbytes=20)
SALT = "scopus-survey-csrf-token"

ENV = EnvConfig()
LOG = Logging(ENV.log_params)

LIMITER = Limiter(key_func=get_remote_address, headers_enabled=True)
RATELIMIT_POLICY = "60 requests per 2 seconds per user (slowapi)"
LIMIT = "60/2seconds"

MAX_AGE = 3600  # 1 hour
SHUTDOWN_TIMEOUT = 5

BASE_URL = f"http://{ENV.host}:{ENV.port}"
CSP = (
    f"default-src 'self' {BASE_URL}; "
    f"script-src 'self' {BASE_URL}/scripts {BASE_URL}/libs "
    "'sha256-jRsTyupz2e+ruvGYICFat6kc2Gm1ilk7iLSex8+pM+I=' "
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js; "
    f"style-src 'self' 'unsafe-inline' {BASE_URL}/styles {BASE_URL}/libs "
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css; "
    f"img-src 'self' data: {BASE_URL}/images {BASE_URL}/svgs "
    "https://fastapi.tiangolo.com/img/favicon.png; "
    f"font-src 'self' {BASE_URL}/fonts; "
    f"connect-src 'self' {BASE_URL}; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
    "object-src 'none'; "
    "child-src 'none'; "
    "frame-src 'none'; "
    "base-uri 'none'"
)
HEADERS = [
    ("Content-Security-Policy", CSP),
    ("Cross-Origin-Opener-Policy", "same-origin"),
    ("Referrer-Policy", "strict-origin-when-cross-origin"),
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("X-XSS-Protection", "1; mode=block"),
]
