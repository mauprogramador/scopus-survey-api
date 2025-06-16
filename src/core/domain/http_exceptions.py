from asyncio import CancelledError
from asyncio import TimeoutError as AsyncTimeoutError
from http import HTTPStatus
from pathlib import Path
from sys import exc_info
from traceback import extract_tb

from aiohttp import ClientError
from fastapi import HTTPException
from itsdangerous import BadData
from pydantic import ValidationError

from src.core.common.messages import SCOPUS_API_ERROR
from src.core.common.types import Errors, ErrorTypes
from src.core.config.scopus import HTTP_CODE_ERRORS
from src.utils.formatters import get_error_message


class HTTPError(HTTPException):
    """Detailed HTTP errors"""

    def __init__(
        self, status: HTTPStatus, message: str, error: ErrorTypes = None
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
    def get_error_details(cls, error: ErrorTypes) -> Errors:
        class_path = f"{type(error).__module__}.{type(error).__qualname__}"
        errors = [{"type": class_path}]
        traceback = exc_info()[2]

        if traceback is not None:
            file_path, line, _, _ = extract_tb(traceback)[-1]
            errors[0].setdefault("file", str(Path(file_path)))
            errors[0].setdefault("line", line)

        if isinstance(error, HTTPException):
            errors[0].setdefault("detail", error.detail)
            errors[0].setdefault("status_code", error.status_code)

        elif isinstance(error, ValidationError):
            errors.extend(error.errors(include_url=False))

        elif isinstance(error, (AsyncTimeoutError, CancelledError)):
            errors[0].setdefault("detail", get_error_message(error))
            errors[0].setdefault("strerror", error.strerror)
            errors[0].setdefault("errno", error.errno)

        elif isinstance(error, ClientError):
            errors[0].setdefault("detail", get_error_message(error))

        elif isinstance(error, BadData):
            errors[0].setdefault("detail", error.message)

        else:
            errors[0].setdefault("detail", get_error_message(error))

        return errors


class Unauthorized(HTTPError):
    """HTTP error status code 401"""

    def __init__(self, message: str, error: Exception = None) -> None:
        """HTTP error status code 401"""
        super().__init__(HTTPStatus.UNAUTHORIZED, message, error)


class NotFound(HTTPError):
    """HTTP error status code 404"""

    def __init__(self, message: str, error: Exception = None) -> None:
        """HTTP error status code 404"""
        super().__init__(HTTPStatus.NOT_FOUND, message, error)


class UnprocessableContent(HTTPError):
    """HTTP error status code 422"""

    def __init__(self, message: str, error: Exception = None) -> None:
        """HTTP error status code 422"""
        super().__init__(HTTPStatus.UNPROCESSABLE_ENTITY, message, error)


class InternalError(HTTPError):
    """HTTP error status code 500"""

    def __init__(self, message: str, error: Exception = None) -> None:
        """HTTP error status code 500"""
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, message, error)


class BadGateway(HTTPError):
    """HTTP error status code 502"""

    def __init__(self, message: str, error: Exception = None) -> None:
        """HTTP error status code 502"""
        super().__init__(HTTPStatus.BAD_GATEWAY, message, error)


class GatewayTimeout(HTTPError):
    """HTTP error status code 504"""

    def __init__(self, message: str, error: Exception = None) -> None:
        """HTTP error status code 504"""
        super().__init__(HTTPStatus.GATEWAY_TIMEOUT, message, error)


class ScopusAPIError(HTTPError):
    """Scopus API HTTP status error exception"""

    def __init__(self, code: int, json: dict, els_status: str) -> None:
        """Scopus API HTTP status error exception"""
        super().__init__(HTTPStatus.BAD_GATEWAY, SCOPUS_API_ERROR)
        self.errors = [
            {
                "els_status": els_status,
                "code_error": HTTP_CODE_ERRORS.get(code, SCOPUS_API_ERROR),
            },
            json,
        ]
