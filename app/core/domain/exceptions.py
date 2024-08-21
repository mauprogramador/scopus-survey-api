from http import HTTPStatus

from requests.models import Response

from app.core.common.messages import INTERRUPT_ERROR, SCOPUS_API_ERROR
from app.core.common.types import Errors
from app.core.config.scopus import API_ERRORS, NULL


class ApplicationError(Exception):
    """Base class for application exceptions"""

    def __init__(self, code: int, message: str, errors: Errors = None) -> None:
        """Base class for application exceptions"""
        super().__init__(message)
        self.code = code
        self.message = message
        self.errors = errors


class InterruptError(ApplicationError):
    """Shutdown signal exit interrupt exception"""

    def __init__(self) -> None:
        """Shutdown signal exit interrupt exception"""
        super().__init__(500, INTERRUPT_ERROR)


class ScopusAPIError(ApplicationError):
    """Scopus Search API HTTP status error exception"""

    def __init__(self, response: Response) -> None:
        """Scopus Search API HTTP status error exception"""
        code = response.status_code
        errors = [
            {
                "status": f"{code} {HTTPStatus(code).phrase}",
                "api_error": API_ERRORS.get(code, NULL),
                "content": response.json(),
            }
        ]
        super().__init__(502, SCOPUS_API_ERROR, errors)
