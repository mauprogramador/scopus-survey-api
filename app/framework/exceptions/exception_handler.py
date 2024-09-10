from json import dumps

from fastapi import Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic_core import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.adapters.presenters.exception_json import ExceptionJSON
from app.core.common.messages import (
    PYDANTIC_ERROR,
    REQUEST_ERROR,
    RESPONSE_ERROR,
    UNEXPECTED_ERROR,
)
from app.core.config.config import LOG
from app.core.config.scopus import NULL
from app.core.domain.exceptions import ApplicationError
from app.framework.exceptions.http_exceptions import HTTPException


class ExceptionHandler:
    """Handles exceptions and returns their JSON representation"""

    @property
    def handlers(self) -> dict:
        return {
            StarletteHTTPException: self.starlette_http_exception,
            FastAPIHTTPException: self.fastapi_http_exception,
            RequestValidationError: self.request_validation_error,
            ResponseValidationError: self.response_validation_error,
            ValidationError: self.pydantic_validation_error,
            HTTPException: self.http_exception,
            ApplicationError: self.application_error,
            Exception: self.common_exception,
        }

    async def starlette_http_exception(
        self, request: Request, exc: StarletteHTTPException
    ) -> ExceptionJSON:
        LOG.error(exc.detail)
        return ExceptionJSON(request, exc.status_code, exc.detail)

    async def fastapi_http_exception(
        self, request: Request, exc: FastAPIHTTPException
    ) -> ExceptionJSON:
        if not exc.detail.isalnum():
            exc.detail = dumps(exc.detail)
        LOG.error(exc.detail)
        return ExceptionJSON(request, exc.status_code, exc.detail)

    async def request_validation_error(
        self, request: Request, exc: RequestValidationError
    ) -> ExceptionJSON:
        first_error: dict = exc.errors()[0]
        message = REQUEST_ERROR.format(first_error.get("msg", NULL))

        LOG.error(message)
        return ExceptionJSON(request, 422, message, exc.errors())

    async def response_validation_error(
        self, request: Request, exc: ResponseValidationError
    ) -> ExceptionJSON:
        first_error: dict = exc.errors()[0]
        message = RESPONSE_ERROR.format(first_error.get("msg", NULL))

        LOG.error(message)
        return ExceptionJSON(request, 500, message, exc.errors())

    async def pydantic_validation_error(
        self, request: Request, exc: ValidationError
    ) -> ExceptionJSON:
        message = PYDANTIC_ERROR.format(exc.error_count(), exc.title)
        LOG.error(message)
        return ExceptionJSON(request, 500, message, exc.errors())

    async def http_exception(
        self, request: Request, exc: HTTPException
    ) -> ExceptionJSON:
        LOG.error(repr(exc), prefix=True)
        return ExceptionJSON(request, exc.code, exc.message)

    async def application_error(
        self, request: Request, exc: ApplicationError
    ) -> ExceptionJSON:
        LOG.error(repr(exc), prefix=True)
        return ExceptionJSON(request, exc.code, exc.message, exc.errors)

    async def common_exception(
        self, request: Request, exc: Exception
    ) -> ExceptionJSON:
        LOG.error(repr(exc), prefix=True)
        return ExceptionJSON(request, 500, UNEXPECTED_ERROR.format(repr(exc)))
