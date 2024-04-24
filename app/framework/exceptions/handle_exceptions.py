from sys import exc_info

from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic_core import ValidationError

from app.core.exceptions import ScopusApiError
from app.framework.exceptions.http_exceptions import HttpException
from app.framework.exceptions.http_responses import (
    BaseExceptionResponse,
    PydanticValidationExceptionResponse,
    ValidationErrorResponse,
)


class ExceptionHandler:
    def __init__(self) -> None:
        self.handlers = {
            RequestValidationError: self.fastapi_validation_error_handler,
            ResponseValidationError: self.fastapi_validation_error_handler,
            ValidationError: self.pydantic_validation_error_handler,
            HttpException: self.http_exception_handler,
            ScopusApiError: self.scopus_api_error_handler,
            Exception: self.exception_handler,
        }

    async def fastapi_validation_error_handler(
        self, _, exception: RequestValidationError | ResponseValidationError
    ):
        response = ValidationErrorResponse(
            message='Validation error in request/response',
            detail=exception.errors(),
        ).handle()
        return JSONResponse(response.model_dump(), 400)

    async def pydantic_validation_error_handler(
        self, _, exception: ValidationError
    ):
        response = PydanticValidationExceptionResponse.make(exception)
        return JSONResponse(response.model_dump(), 500)

    async def http_exception_handler(self, _, exception: HttpException):
        return JSONResponse(exception.to_dict(), exception.status_code)

    async def scopus_api_error_handler(self, _, exception: ScopusApiError):
        return JSONResponse(exception.to_dict(), exception.status_code)

    async def exception_handler(self, _, exception: Exception):
        exception_type, exception_value, _ = exc_info()
        exception_name = getattr(exception_type, '__name__', 'Exception')
        message = (
            f'Unexpected Error <{exception_name}({exception_value}): '
            f'Args: {exception.args}>'
        )
        response = BaseExceptionResponse(message=message)
        return JSONResponse(response.model_dump(), 500)
