from secrets import token_hex

from app.core.common.types import Token
from app.utils.logging import ApplicationLogger
from app.utils.signal_handler import ShutdownSignalHandler
from app.core.config.env import EnvConfig


TOKEN = Token.validate_strings(token_hex(nbytes=16))
SECRET_KEY = Token.validate_strings(token_hex(nbytes=16))

SHUTDOWN = ShutdownSignalHandler()
ENV = EnvConfig()
LOG = ApplicationLogger(ENV.log_config)

TOKEN_HEADER = "X-Access-Token"
CSV_HEADER = "X-CSV-Filename"
USER_API_KEY_HEADER = "X-User-API-Key"

API_KEY_QUERY = "apikey"
KEYWORDS_QUERY = "keywords"

DIRECTORY = "csv"
FILE = "articles.csv"

APP = "app.framework.fastapi.main:app"


SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; base-uri 'self'; connect-src 'self'; "
        "child-src 'none'; frame-src 'none'; frame-ancestors 'none'; "
        "form-action 'self'; img-src 'self' data: https://fastapi."
        "tiangolo.com/img/favicon.png; style-src 'self' 'unsafe-inline' "
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui."
        "css; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr"
        ".net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"
    ),
    "Cross-Origin-Opener-Policy": "same-origin",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
}

CSV_RESPONSE = {
    200: {
        "description": "Return the CSV file",
        "content": {
            "text/csv": {
                "example": (
                    "Article Preview Page URL;Scopus ID;Authors;Title;"
                    "Publication Name;Abstract;Date;Electronic ID;DOI;"
                    "Volume;Citations\nhttps://www.scopus.com/inward/"
                    "record.uri?partnerID=HzOxMe3b&scp=85183327527&origin"
                    "=inward;SCOPUS_ID:85183327527;Roman A.;Enhancing "
                    "Georeferencing and Mosaicking Techniques over Water "
                    "Surfaces with High-Resolution Unmanned Aerial Vehicle "
                    "(UAV) Imagery;Remote Sensing;null;2024-01-01;2-s2.0-85"
                    "183327527;10.3390/rs16020290;16;11"
                ),
            }
        },
    },
}
HTML_RESPONSE = {
    200: {
        "description": "",
        "content": {
            "text/html": {
                "example": "<html>...</html>",
            }
        }
    }
}
