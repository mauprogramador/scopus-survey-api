from typing import Any
from fastapi import HTTPException as FastAPIHTTPException
from pydantic import BaseModel

from app.core.common.types import Errors


class BaseExceptionResponse(BaseModel):
    """Base class for exceptions response"""

    success: bool = False
    code: int
    message: str
    request: dict[str, Any]
    errors: Errors = None
    timestamp: str


class HTTPException(FastAPIHTTPException):
    """Base class for HTTP exceptions"""

    def __init__(self, code: int, message: str) -> None:
        """Base class for HTTP exceptions"""
        super().__init__(code, message)
        self.code = code
        self.message = message


class Unauthorized(HTTPException):
    """HTTP error status code 401"""

    def __init__(self, message: str) -> None:
        """HTTP error status code 401"""
        super().__init__(401, message)


class NotFound(HTTPException):
    """HTTP error status code 404"""

    def __init__(self, message: str) -> None:
        """HTTP error status code 404"""
        super().__init__(404, message)


class UnprocessableContent(HTTPException):
    """HTTP error status code 422"""

    def __init__(self, message: str) -> None:
        """HTTP error status code 422"""
        super().__init__(422, message)


class InternalError(HTTPException):
    """HTTP error status code 500"""

    def __init__(self, message: str) -> None:
        """HTTP error status code 500"""
        super().__init__(500, message)


class BadGateway(HTTPException):
    """HTTP error status code 502"""

    def __init__(self, message: str) -> None:
        """HTTP error status code 502"""
        super().__init__(502, message)


class GatewayTimeout(HTTPException):
    """HTTP error status code 504"""

    def __init__(self, message: str) -> None:
        """HTTP error status code 504"""
        super().__init__(504, message)


class Forbidden(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(403, message)


class FailedDependency(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(424, message)
