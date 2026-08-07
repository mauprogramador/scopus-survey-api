from http import HTTPStatus

from src.adapters.formatters import get_error_details
from src.core.domain.types import ExcMsg


class BaseHTTPError(Exception):
    """Detailed HTTP errors"""

    def __init__(
        self, status: HTTPStatus, message: ExcMsg, cause: Exception = None
    ) -> None:
        """Detailed HTTP errors"""
        self.status_code = status
        self.message = message

        if cause is not None:
            self.details = [get_error_details(cause)]
        else:
            self.details = None

    def __str__(self) -> str:
        if not self.details:
            return f"{self.status_code}: {self.message}"
        return f"{self.status_code}: {self.message}. {self.details!r}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(status_code={self.status_code}, "
            f"message={self.message}, details={self.details!r})"
        )


class ResourceNotFoundError(BaseHTTPError):
    """HTTP error status code 404"""

    def __init__(self, message: ExcMsg) -> None:
        """HTTP error status code 404"""
        super().__init__(HTTPStatus.NOT_FOUND, message)


class DataSumMismatchError(BaseHTTPError):
    """HTTP error status code 502"""

    def __init__(self, message: ExcMsg, cause: Exception = None) -> None:
        """HTTP error status code 502"""
        super().__init__(HTTPStatus.BAD_GATEWAY, message, cause)
