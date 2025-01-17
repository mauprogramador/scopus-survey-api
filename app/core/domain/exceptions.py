from http import HTTPStatus

from app.core.common.messages import INTERRUPT_ERROR
from app.core.common.types import Errors
from app.core.config.scopus import HTTP_CODE_ERRORS


class ApplicationError(Exception):
    """Base class for application exceptions"""

    def __init__(self, code: int, message: str, errors: Errors = None) -> None:
        """Base class for application exceptions"""
        super().__init__(message)
        self.code = code
        self.message = message
        self.errors = errors


class InterruptError(ApplicationError):
    """Shutdown/exit interruption signal exception"""

    def __init__(self) -> None:
        """Shutdown/exit interruption signal exception"""
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, INTERRUPT_ERROR)


class ScopusAPIError(ApplicationError):
    """Scopus Search API HTTP status error exception"""

    def __init__(
        self, code: int, json: dict, els_status: str, message: str
    ) -> None:
        """Scopus Search API HTTP status error exception"""
        errors = [
            {
                "els_status": els_status,
                "code_error": HTTP_CODE_ERRORS.get(code, "Scopus API Error"),
                "scopus_json": json,
            }
        ]
        super().__init__(HTTPStatus.BAD_GATEWAY, message, errors)
