import asyncio
from datetime import datetime, timezone
from http import HTTPStatus
from json import JSONDecodeError

import aiohttp
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from itsdangerous import BadData, BadSignature, SignatureExpired
from pydantic import ValidationError

from src.core.common.types import Json
from src.core.config.scopus import SCOPUS_DOCS
from src.core.data.enums import ExcMsg


def get_error_message(exc: Exception) -> str:
    if exc.args and exc.args[0] and isinstance(exc.args[0], str):
        return exc.args[0]
    if getattr(exc, "message", None) is not None:
        return getattr(exc, "message")
    if getattr(exc, "detail", None) is not None:
        return getattr(exc, "detail")
    return repr(exc)


def get_error_details(exc: Exception) -> list[Json]:
    base_error = {
        "type": f"{type(exc).__module__}.{type(exc).__qualname__}",
        "message": get_error_message(exc),
    }
    details = [base_error]

    if isinstance(exc, ValidationError):
        pydantic_errors = exc.errors(include_url=False)
        details[0]["message"] = pydantic_errors[0].get("msg", exc.title)
        details.extend(pydantic_errors)

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
            self.details = get_error_details(exc)
        else:
            self.details = None

        super().__init__(status, message)


class Unauthorized(HTTPError):
    """HTTP error status code 401"""

    def __init__(self, message: ExcMsg, exc: Exception = None) -> None:
        """HTTP error status code 401"""
        super().__init__(HTTPStatus.UNAUTHORIZED, message, exc)

        if isinstance(exc, (SignatureExpired, BadSignature, BadData)):
            self.details[0]["message"] = exc.message
            date_signed = getattr(exc, "date_signed", None)

            if isinstance(date_signed, datetime):
                date_signed = date_signed.replace(
                    tzinfo=timezone.utc
                ).isoformat(timespec="seconds")

            signature_detail = {
                "payload": getattr(exc, "payload", None),
                "date_signed": date_signed,
            }
            self.details.append(signature_detail)


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


class ServiceUnavailable(HTTPError):
    """HTTP error status code 503"""

    def __init__(self, message: ExcMsg, exc: Exception = None) -> None:
        """HTTP error status code 503"""
        super().__init__(HTTPStatus.SERVICE_UNAVAILABLE, message, exc)


class GatewayTimeout(HTTPError):
    """HTTP error status code 504"""

    def __init__(self, message: ExcMsg, exc: Exception = None) -> None:
        """HTTP error status code 504"""
        super().__init__(HTTPStatus.GATEWAY_TIMEOUT, message, exc)

        if isinstance(exc, asyncio.TimeoutError):
            timeout_detail = {"strerror": exc.strerror, "errno": exc.errno}
            self.details.append(timeout_detail)


class BadGatewayContent(HTTPError):
    """HTTP error status code 502"""

    def __init__(self, message: ExcMsg, exc: Exception, body: str) -> None:
        """HTTP error status code 502"""
        super().__init__(HTTPStatus.BAD_GATEWAY, message, exc)
        body_detail: Json = {"raw_body": body}

        if isinstance(exc, aiohttp.ContentTypeError):
            content_type_detail: Json = {
                "message": exc.message,
                "status_code": exc.status,
                "path": exc.request_info.url.path,
            }
            body_detail.update(content_type_detail)

        elif isinstance(exc, JSONDecodeError):
            json_decode_detail: Json = {
                "message": exc.msg,
                "doc": exc.doc,
                "pos": exc.pos,
                "lineno": exc.lineno,
                "colno": exc.colno,
            }
            body_detail.update(json_decode_detail)

        self.details.append(body_detail)


class ScopusAPIError(HTTPError):
    """Scopus API HTTP status error 502 exception"""

    def __init__(
        self,
        code: int,
        headers: Json,
        scopus_error: Json,
        body: Json,
    ) -> None:
        """Scopus API HTTP status error 502 exception"""
        # Use ExcMsg as a mock replacement only
        super().__init__(HTTPStatus.BAD_GATEWAY, ExcMsg.SCOPUS_API_ERROR)
        self.message = scopus_error["text"]
        self.detail = scopus_error["text"]

        scopus_api_detail = {
            **headers,
            "status_code": code,
            "status": HTTPStatus(code).phrase,
            "error_code": scopus_error["code"],
            "error_text": scopus_error["text"],
            "docs": SCOPUS_DOCS,
        }
        self.details: list[Json] = [scopus_api_detail, body]
