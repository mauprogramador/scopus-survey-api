from http import HTTPStatus

from requests.models import Response

from app.core.common.messages import INTERRUPT_ERROR
from app.core.common.types import Errors
from app.core.config.config import LOG
from app.core.config.scopus import (
    API_ERRORS,
    FURTHER_INFO_LINK,
    NULL,
    QUOTA_WARNING,
    RATE_LIMIT_WARNING,
)
from app.core.data.serializers import ScopusQuotaRateLimit


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
        super().__init__(500, INTERRUPT_ERROR)


class ScopusAPIError(ApplicationError):
    """Scopus Search API HTTP status error exception"""

    def __init__(self, response: Response, message: str) -> None:
        """Scopus Search API HTTP status error exception"""
        code = response.status_code
        api_error = API_ERRORS.get(code, NULL)

        if code == 429:
            status = ScopusQuotaRateLimit.model_validate(response)

            if status.quota_exceeded:
                LOG.error(QUOTA_WARNING.format(status.reset_datetime))

            if status.rate_limit_exceeded:
                api_error = RATE_LIMIT_WARNING
                LOG.error(RATE_LIMIT_WARNING)

            LOG.info(FURTHER_INFO_LINK)

        errors = [
            {
                "status": f"{code} {HTTPStatus(code).phrase}",
                "api_error": api_error,
                "content": response.json(),
            }
        ]

        super().__init__(502, message, errors)
