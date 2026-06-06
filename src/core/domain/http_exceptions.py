import asyncio
import sys
import traceback
from http import HTTPStatus
from json import JSONDecodeError

import aiohttp
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from itsdangerous import BadData, BadSignature, SignatureExpired
from pydantic import ValidationError

from src.core.common.types import Json
from src.core.config.scopus import SCOPUS_DOCS
from src.core.data.enums import ExcMsg


_FRAME = traceback.FrameSummary(__file__, 1, "<http_exceptions>")
_ROOT_PATH = "/scopus-survey-api"


def get_error_message(exc: Exception) -> str:
    if exc.args and exc.args[0] and isinstance(exc.args[0], str):
        return exc.args[0]
    if getattr(exc, "message", None) is not None:
        return getattr(exc, "message")
    if getattr(exc, "detail", None) is not None:
        return getattr(exc, "detail")
    return repr(exc)


def get_error_details(error: Exception) -> list[Json]:
    exc_trace = sys.exc_info()[2]
    frame = traceback.extract_tb(exc_trace)[-1] if exc_trace else _FRAME

    file = frame.filename
    if file.count(_ROOT_PATH):
        file = file[file.index(_ROOT_PATH) :]

    base_error = {
        "type": f"{type(error).__module__}.{type(error).__qualname__}",
        "message": get_error_message(error),
        "file": file,
        "line": frame.lineno,
    }
    errors = [base_error]

    if isinstance(error, ValidationError):
        pydantic_errors = error.errors(include_url=False)
        errors[0]["message"] = pydantic_errors[0].get("msg", error.title)
        errors.extend(pydantic_errors)

    return errors


class HTTPError(FastAPIHTTPException):
    """Detailed HTTP errors"""

    def __init__(
        self, status: HTTPStatus, message: ExcMsg, error: Exception = None
    ) -> None:
        """Detailed HTTP errors"""
        self.status = status
        self.message = message

        if error is not None:
            self.errors = get_error_details(error)
        else:
            self.errors = None

        super().__init__(status, message)


class Unauthorized(HTTPError):
    """HTTP error status code 401"""

    def __init__(self, message: ExcMsg, error: Exception = None) -> None:
        """HTTP error status code 401"""
        super().__init__(HTTPStatus.UNAUTHORIZED, message, error)

        if isinstance(error, (SignatureExpired, BadSignature, BadData)):
            self.errors[0]["message"] = error.message

            if isinstance(error, (SignatureExpired, BadSignature)):
                signature_details = {"payload": error.payload}

                if isinstance(error, SignatureExpired):
                    signature_details["date_signed"] = error.date_signed

                self.errors.append(signature_details)


class NotFound(HTTPError):
    """HTTP error status code 404"""

    def __init__(self, message: ExcMsg) -> None:
        """HTTP error status code 404"""
        super().__init__(HTTPStatus.NOT_FOUND, message)


class InternalError(HTTPError):
    """HTTP error status code 500"""

    def __init__(self, message: ExcMsg, error: Exception = None) -> None:
        """HTTP error status code 500"""
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, message, error)


class BadGateway(HTTPError):
    """HTTP error status code 502"""

    def __init__(self, message: ExcMsg, error: Exception = None) -> None:
        """HTTP error status code 502"""
        super().__init__(HTTPStatus.BAD_GATEWAY, message, error)


class ServiceUnavailable(HTTPError):
    """HTTP error status code 503"""

    def __init__(self, message: ExcMsg, error: Exception = None) -> None:
        """HTTP error status code 503"""
        super().__init__(HTTPStatus.SERVICE_UNAVAILABLE, message, error)


class GatewayTimeout(HTTPError):
    """HTTP error status code 504"""

    def __init__(self, message: ExcMsg, error: Exception = None) -> None:
        """HTTP error status code 504"""
        super().__init__(HTTPStatus.GATEWAY_TIMEOUT, message, error)

        if isinstance(error, asyncio.TimeoutError):
            details = {"strerror": error.strerror, "errno": error.errno}
            self.errors.append(details)


class BadGatewayContent(HTTPError):
    """HTTP error status code 502"""

    def __init__(self, message: ExcMsg, error: Exception, body: str) -> None:
        """HTTP error status code 502"""
        super().__init__(HTTPStatus.BAD_GATEWAY, message, error)
        details: Json = {"raw_body": body}

        if isinstance(error, aiohttp.ContentTypeError):
            content_details: Json = {
                "message": error.message,
                "status_code": error.status,
                "url": str(error.request_info.url),
                "headers": (error.headers.items() if error.headers else None),
            }
            details.update(content_details)

        elif isinstance(error, JSONDecodeError):
            json_details: Json = {
                "message": error.msg,
                "doc": error.doc,
                "pos": error.pos,
                "lineno": error.lineno,
                "colno": error.colno,
            }
            details.update(json_details)

        self.errors.append(details)


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

        error = {
            **headers,
            "status_code": code,
            "status": HTTPStatus(code).phrase,
            "error_code": scopus_error["code"],
            "error_text": scopus_error["text"],
            "docs": SCOPUS_DOCS,
        }
        self.errors: list[Json] = [error, body]
