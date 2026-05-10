from contextvars import ContextVar
from pathlib import Path

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.config.env import EnvConfig
from src.utils.logging import Logging


APP = "src.framework.fastapi.main:app"
PREFIX = "/v2/scopus-survey"

TRACE_ID_CTX: ContextVar[str] = ContextVar("trace_id")
SERVER: ContextVar[str] = ContextVar("server")

DIRECTORY = Path("csv")
FILE = "docs.csv"

SALT = "scopus-survey-csrf-token"
MAX_AGE = 3600  # 1 hour

ENV = EnvConfig()
LOG = Logging(ENV.log_params)

LIMITER = Limiter(key_func=get_remote_address, headers_enabled=True)
RATELIMIT_POLICY = "60 requests per 2 seconds per user (slowapi)"
LIMIT = "60/2seconds"

INSTITUTION = (
    "Instituto Federal de Educação, Ciência e Tecnologia de"
    " Mato Grosso do Sul (IFMS) - Campus Três Lagoas"
)
META_INFO = {
    "title": "Scopus Survey API",
    "repository": "https://github.com/mauprogramador/scopus-survey-api",
    "documentation": "https://mauprogramador.github.io/scopus-survey-api",
    "institution": INSTITUTION,
    "modified": "2026-00-00",
    "created": "2024-02-26",
    "date": "2025-08-09",
    "year": "2024",
    "format": "text/html",
    "type": "software",
}

BASE_URL = f"http://{ENV.host}:{ENV.port}"
CSP = (
    f"default-src 'self' {BASE_URL}; "
    f"script-src 'self' {BASE_URL}/scripts {BASE_URL}/libs "
    "'sha256-jRsTyupz2e+ruvGYICFat6kc2Gm1ilk7iLSex8+pM+I=' "
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js; "
    f"style-src 'self' 'unsafe-inline' {BASE_URL}/styles {BASE_URL}/libs "
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css "
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css.map; "
    f"img-src 'self' data: {BASE_URL}/images {BASE_URL}/svgs "
    "https://fastapi.tiangolo.com/img/favicon.png; "
    f"font-src 'self' {BASE_URL}/fonts; "
    f"connect-src 'self' {BASE_URL} https://cdn.jsdelivr.net; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
    "object-src 'none'; "
    "child-src 'none'; "
    "frame-src 'none'; "
    "base-uri 'none'"
)
HEADERS = {
    "Content-Security-Policy": CSP,
    "Cross-Origin-Opener-Policy": "same-origin",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
}
