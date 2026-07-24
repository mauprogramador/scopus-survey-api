from datetime import datetime, timezone
from http import HTTPStatus
from json import JSONDecodeError

import aiohttp
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from itsdangerous import BadSignature, SignatureExpired
from pydantic import ValidationError

from src.core.domain.enums import ExcMsg
from src.core.domain.types import Json
from src.infra.config.scopus import SCOPUS_DOCS


def get_error_message(exc: Exception) -> str:
    if getattr(exc, "message", None) is not None:
        return getattr(exc, "message")
    if getattr(exc, "detail", None) is not None:
        return getattr(exc, "detail")
    if exc.args and exc.args[0] and isinstance(exc.args[0], str):
        return exc.args[0]
    return repr(exc)


def _error_details(exc: Exception) -> Json:
    details = {
        "type": f"{type(exc).__module__}.{type(exc).__qualname__}",
        "message": get_error_message(exc),
    }

    if isinstance(exc, ValidationError):
        pydantic_errors = exc.errors(include_url=False)
        details["message"] = pydantic_errors[0].get("msg", exc.title)
        details["errors"] = pydantic_errors

    return details


def get_error_details(exc: Exception) -> Json:
    details = _error_details(exc)

    cause = exc.__cause__ or exc.__context__
    if cause:
        details["cause"] = _error_details(cause)

    return details


class HTTPError(FastAPIHTTPException):
    """Detailed HTTP errors"""

    def __init__(
        self, status: HTTPStatus, message: ExcMsg, exc: Exception = None
    ) -> None:
        """Detailed HTTP errors"""
        self.status = status
        self.message = message

        if exc is not None:
            self.details = [get_error_details(exc)]
        else:
            self.details = None

        super().__init__(status, message)


class Unauthorized(HTTPError):
    """HTTP error status code 401"""

    def __init__(self, message: ExcMsg, exc: Exception = None) -> None:
        """HTTP error status code 401"""
        super().__init__(HTTPStatus.UNAUTHORIZED, message, exc)

        if isinstance(exc, BadSignature):
            self.details[0]["signature"] = {"payload": exc.payload}

        if isinstance(exc, SignatureExpired):
            date_signed = exc.date_signed

            if isinstance(date_signed, datetime):
                date_signed = date_signed.replace(
                    tzinfo=timezone.utc  # e.g. 2026-01-01T00:00:00Z
                ).isoformat(timespec="seconds")

            self.details[0]["signature"]["date_signed"] = date_signed


class NotFound(HTTPError):
    """HTTP error status code 404"""

    def __init__(self, message: ExcMsg) -> None:
        """HTTP error status code 404"""
        super().__init__(HTTPStatus.NOT_FOUND, message)


class InternalError(HTTPError):
    """HTTP error status code 500"""

    def __init__(self, message: ExcMsg, exc: Exception = None) -> None:
        """HTTP error status code 500"""
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, message, exc)


class BadGateway(HTTPError):
    """HTTP error status code 502"""

    def __init__(self, message: ExcMsg, exc: Exception = None) -> None:
        """HTTP error status code 502"""
        super().__init__(HTTPStatus.BAD_GATEWAY, message, exc)


class GatewayTimeout(HTTPError):
    """HTTP error status code 504"""

    def __init__(self, message: ExcMsg, exc: Exception = None) -> None:
        """HTTP error status code 504"""
        super().__init__(HTTPStatus.GATEWAY_TIMEOUT, message, exc)


class BadGatewayContent(HTTPError):
    """HTTP error status code 502"""

    _TRUNCATE_SIZE = 1000

    def __init__(self, message: ExcMsg, exc: Exception, body: str) -> None:
        """HTTP error status code 502"""
        super().__init__(HTTPStatus.BAD_GATEWAY, message, exc)

        if len(body) > self._TRUNCATE_SIZE:
            self.details[0]["body"] = body[:997] + "..."  # truncate
        else:
            self.details[0]["body"] = body

        if isinstance(exc, aiohttp.ContentTypeError):
            content_type_detail: Json = {
                "message": exc.message,
                "status_code": exc.status,
                "resource": exc.request_info.url.path,
            }
            self.details[0]["error"] = content_type_detail

        elif isinstance(exc, JSONDecodeError):
            json_decode_detail: Json = {
                "message": exc.msg,
                "pos": exc.pos,
                "lineno": exc.lineno,
                "colno": exc.colno,
            }
            self.details[0]["error"] = json_decode_detail


class ScopusAPIError(HTTPError):
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
