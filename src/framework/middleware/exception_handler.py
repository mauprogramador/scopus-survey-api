from http import HTTPStatus

from fastapi import Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic_core import PydanticUndefined, ValidationError
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.adapters.presenters.error_response import ErrorJSON
from src.core.common.error_messages import INTERNAL_ERROR
from src.core.common.types import Json
from src.core.config.config import LOG
from src.core.domain.http_exceptions import HTTPError, ScopusAPIError


class ExceptionHandler:
    """Handles exceptions and returns their JSON representation"""

    @property
    def handlers(self) -> dict:
        return {
            HTTPError: self.custom_http_error,
            ScopusAPIError: self.scopus_api_error,
            StarletteHTTPException: self.starlette_http_exception,
            FastAPIHTTPException: self.starlette_http_exception,
            RequestValidationError: self.fastapi_validation_error,
            ResponseValidationError: self.fastapi_validation_error,
            ValidationError: self.pydantic_validation_error,
            RateLimitExceeded: self.rate_limit_error,
        }

    def _undefined_filter(self, item: Json) -> Json:
        if "input" in item and item["input"] is PydanticUndefined:
            item["input"] = "PydanticUndefined"
        return item

    def _exception_filter(self, item: Json) -> Json:
        if "ctx" in item and "error" in item["ctx"]:
            if isinstance(item["ctx"]["error"], Exception):
                item["ctx"]["error"] = type(item["ctx"]["error"]).__name__
        return item

    async def custom_http_error(
        self, request: Request, exc: HTTPError
    ) -> ErrorJSON:
        LOG.error(exc.detail)
        LOG.exception(exc)
        return ErrorJSON(
            request,
            exc.status_code,
            exc.detail,
            exc.errors,
        )

    async def scopus_api_error(
        self, request: Request, exc: ScopusAPIError
    ) -> ErrorJSON:
        LOG.error(exc.message)
        LOG.exception(exc)
        return ErrorJSON(request, exc.status_code, exc.message, exc.errors)

    async def starlette_http_exception(
        self,
        request: Request,
        exc: StarletteHTTPException | FastAPIHTTPException,
    ) -> ErrorJSON:
        LOG.error(exc.detail)
        LOG.exception(exc)
        return ErrorJSON(request, exc.status_code, exc.detail)

    async def fastapi_validation_error(
        self,
        request: Request,
        exc: RequestValidationError | ResponseValidationError,
    ) -> ErrorJSON:
        errors = list(map(self._exception_filter, exc.errors()))
        message = errors[0].get("msg", INTERNAL_ERROR)

        LOG.error(message)
        LOG.exception(exc)

        return ErrorJSON(
            request,
            HTTPStatus.UNPROCESSABLE_ENTITY,
            message,
            errors,
        )

    async def pydantic_validation_error(
        self, request: Request, exc: ValidationError
    ) -> ErrorJSON:
        errors = list(
            map(self._undefined_filter, exc.errors(include_url=False))
        )
        message = errors[0].get("msg", exc.title)

        LOG.error(message)
        LOG.exception(exc)

        return ErrorJSON(
            request,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            message,
            errors,
        )

    async def rate_limit_error(
        self, request: Request, exc: RateLimitExceeded
    ) -> ErrorJSON:
        message = f"Request rate limit of {exc.detail} exceeded"
        LOG.error(message)
        LOG.exception(exc)
        return ErrorJSON(
            request,
            HTTPStatus.TOO_MANY_REQUESTS,
            message,
        )
