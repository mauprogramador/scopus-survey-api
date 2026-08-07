from datetime import datetime, timezone
from http import HTTPStatus
from json import JSONDecodeError

import aiohttp
from itsdangerous import BadSignature, SignatureExpired

from src.adapters.exceptions import BaseHTTPError
from src.core.domain.types import ExcMsg, Json
from src.infra.config.scopus import SCOPUS_DOCS


class CSRFAuthenticationError(BaseHTTPError):
    """HTTP error status code 401"""

    def __init__(self, message: ExcMsg, cause: Exception = None) -> None:
        """HTTP error status code 401"""
        super().__init__(HTTPStatus.UNAUTHORIZED, message, cause)

        if isinstance(cause, BadSignature):
            self.details[0]["signature"] = {"payload": cause.payload}

        if isinstance(cause, SignatureExpired):
            date_signed = cause.date_signed

            if isinstance(date_signed, datetime):
                date_signed = date_signed.replace(
                    tzinfo=timezone.utc  # e.g. 2026-01-01T00:00:00Z
                ).isoformat(timespec="seconds")

            self.details[0]["signature"]["date_signed"] = date_signed


class UncaughtError(BaseHTTPError):
    """HTTP error status code 500"""

    def __init__(self, message: ExcMsg, cause: Exception = None) -> None:
        """HTTP error status code 500"""
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, message, cause)


class TasksCancellationError(BaseHTTPError):
    """HTTP error status code 500"""

    def __init__(self, message: ExcMsg, cause: Exception = None) -> None:
        """HTTP error status code 500"""
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, message, cause)


class APIValidationError(BaseHTTPError):
    """HTTP error status code 500"""

    def __init__(self, message: ExcMsg, cause: Exception = None) -> None:
        """HTTP error status code 500"""
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, message, cause)


class APITimeoutError(BaseHTTPError):
    """HTTP error status code 504"""

    def __init__(self, message: ExcMsg, cause: Exception = None) -> None:
        """HTTP error status code 504"""
        super().__init__(HTTPStatus.GATEWAY_TIMEOUT, message, cause)


class APIConnectionError(BaseHTTPError):
    """HTTP error status code 502"""

    def __init__(self, message: ExcMsg, cause: Exception = None) -> None:
        """HTTP error status code 502"""
        super().__init__(HTTPStatus.BAD_GATEWAY, message, cause)


class APIRequestError(BaseHTTPError):
    """HTTP error status code 502"""

    def __init__(self, message: ExcMsg, cause: Exception = None) -> None:
        """HTTP error status code 502"""
        super().__init__(HTTPStatus.BAD_GATEWAY, message, cause)


class APIContentError(BaseHTTPError):
    """HTTP error status code 502"""

    _TRUNCATE_SIZE = 1000

    def __init__(self, message: ExcMsg, cause: Exception, body: str) -> None:
        """HTTP error status code 502"""
        super().__init__(HTTPStatus.BAD_GATEWAY, message, cause)

        if len(body) > self._TRUNCATE_SIZE:
            self.details[0]["body"] = body[:997] + "..."  # truncate
        else:
            self.details[0]["body"] = body

        if isinstance(cause, aiohttp.ContentTypeError):
            content_type_detail: Json = {
                "message": cause.message,
                "status_code": cause.status,
                "resource": cause.request_info.url.path,
            }
            self.details[0]["error"] = content_type_detail

        elif isinstance(cause, JSONDecodeError):
            json_decode_detail: Json = {
                "message": cause.msg,
                "pos": cause.pos,
                "lineno": cause.lineno,
                "colno": cause.colno,
            }
            self.details[0]["error"] = json_decode_detail


class APIResponseError(BaseHTTPError):
    """Scopus API HTTP status error 502 exception"""

    def __init__(
        self,
        code: int,
        headers: Json,
        scopus_error: Json,
    ) -> None:
        """Scopus API HTTP status error 502 exception"""
        # Use ExcMsg as a mock replacement only
        super().__init__(HTTPStatus.BAD_GATEWAY, ExcMsg.SCOPUS_API_ERROR)
        self.message = scopus_error["text"]
        self.detail = scopus_error["text"]

        scopus_details = {
            **headers,
            "status_code": code,
            "error_code": scopus_error["code"],
            "error_text": scopus_error["text"],
            "docs": SCOPUS_DOCS,
        }
        self.details = [scopus_details]
