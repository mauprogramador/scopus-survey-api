from sys import exc_info

from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic_core import ValidationError

from app.exceptions.http_exceptions import HttpException
from app.exceptions.http_responses import (
    BaseExceptionResponse,
    PydanticValidationExceptionResponse,
    ValidationErrorResponse,
)


async def fastapi_validation_error_handler(
    _, exception: RequestValidationError | ResponseValidationError
):
    response = ValidationErrorResponse(
        message='Validation error in request/response',
        detail=exception.errors(),
    ).handle()
    return JSONResponse(response.model_dump(), 400)


async def pydantic_validation_error_handler(_, exception: ValidationError):
    response = PydanticValidationExceptionResponse.make(exception)
    return JSONResponse(response.model_dump(), 500)


async def http_exception_handler(_, exception: HttpException):
    return JSONResponse(exception.to_dict(), exception.status_code)


async def exception_handler(_, exception: Exception):
    exception_type, exception_value, _ = exc_info()
    exception_name = getattr(exception_type, '__name__', 'Exception')
    message = (
        f'Unexpected Error <{exception_name}({exception_value}): '
        f'Args: {exception.args}>'
    )
    response = BaseExceptionResponse(message=message)
    return JSONResponse(response.model_dump(), 500)


HANDLERS = {
    RequestValidationError: fastapi_validation_error_handler,
    ResponseValidationError: fastapi_validation_error_handler,
    ValidationError: pydantic_validation_error_handler,
    HttpException: http_exception_handler,
    Exception: exception_handler,
}
