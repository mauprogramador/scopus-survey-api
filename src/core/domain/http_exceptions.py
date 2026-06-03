from asyncio import TimeoutError as AsyncTimeoutError
from http import HTTPStatus
from sys import exc_info
from traceback import FrameSummary, extract_tb

from aiohttp import ClientResponseError
from fastapi import HTTPException
from itsdangerous import BadData
from pydantic import ValidationError

from src.core.common.types import Json
from src.core.config.config import LOG
from src.core.config.scopus import SCOPUS_DOCS, SCOPUS_ERRORS
from src.core.data.enums import ExcMsg


class HTTPError(HTTPException):
    """Detailed HTTP errors"""

    _FRAME = FrameSummary(__file__, 1, "<http_exceptions>")
    _ROOT_PATH = "/scopus-survey-api"

    def __init__(
        self, status: HTTPStatus, message: ExcMsg, error: Exception = None
    ) -> None:
        """Detailed HTTP errors"""
        self.status = status
        self.message = message

        if error is not None:
            self.errors = self.get_error_details(error)
        else:
            self.errors = None

        super().__init__(status, message)

    @classmethod
    def get_error_details(cls, error: Exception) -> list[Json]:
        traceback = exc_info()[2]
        frame = extract_tb(traceback)[-1] if traceback else cls._FRAME

        file = frame.filename
        if file.count(cls._ROOT_PATH):
            file = file[file.index(cls._ROOT_PATH) :]

        base_error = {
            "type": f"{type(error).__module__}.{type(error).__qualname__}",
            "detail": LOG.error_message(error, UNEXPECTED_ERROR),
            "file": file,
            "line": frame.lineno,
        }
        errors = [base_error]

        if isinstance(error, HTTPException):
            errors[0]["detail"] = error.detail
            errors[0]["status_code"] = error.status_code

        elif isinstance(error, ValidationError):
            pydantic_errors = error.errors(include_url=False)
            errors[0]["detail"] = pydantic_errors[0].get("msg", error.title)
            errors.extend(pydantic_errors)

        elif isinstance(error, AsyncTimeoutError):
            errors[0]["strerror"] = error.strerror
            errors[0]["errno"] = error.errno

        elif isinstance(error, (BadData, ClientResponseError)):
            errors[0]["detail"] = error.message

        return errors


class Unauthorized(HTTPError):
    """HTTP error status code 401"""

    def __init__(self, message: ExcMsg, error: Exception = None) -> None:
        """HTTP error status code 401"""
        super().__init__(HTTPStatus.UNAUTHORIZED, message, error)


class NotFound(HTTPError):
    """HTTP error status code 404"""

    def __init__(self, message: ExcMsg) -> None:
        """HTTP error status code 404"""
        super().__init__(HTTPStatus.NOT_FOUND, message, error)


class UnprocessableContent(HTTPError):
    """HTTP error status code 422"""

    def __init__(self, message: str, error: Exception = None) -> None:
        """HTTP error status code 422"""
        super().__init__(HTTPStatus.UNPROCESSABLE_ENTITY, message, error)


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


class BadGatewayContent(HTTPError):
    """HTTP error status code 502"""

    def __init__(self, message: ExcMsg, error: Exception, body: str) -> None:
        """HTTP error status code 502"""
        super().__init__(HTTPStatus.BAD_GATEWAY, message, error)
        self.errors.append({"body": body})


class ScopusAPIError(HTTPError):
    """Scopus API HTTP status error 502 exception"""

    def __init__(
        self, message: str, code: int, body: Json, headers: Json
    ) -> None:
        """Scopus API HTTP status error 502 exception"""
        # Use ExcMsg as a mock replacement only
        super().__init__(HTTPStatus.BAD_GATEWAY, ExcMsg.SCOPUS_API_ERROR)

        code_error = SCOPUS_ERRORS.get(HTTPStatus(code), SCOPUS_API_ERROR)
        self.errors: list[Json] = [
            {
                **headers,
                "els_status": message,
                "code_error": code_error,
                "docs": SCOPUS_DOCS,
            },
            body,
        ]
