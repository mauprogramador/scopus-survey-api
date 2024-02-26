from .handle_exceptions import HANDLERS
from .http_exceptions import (
    FailedDependency,
    Forbidden,
    HttpException,
    InternalError,
    NotFound,
    ScopusApiError,
    Unauthorized,
    UnprocessableContent,
)
from .http_responses import (
    BaseExceptionResponse,
    PydanticValidationExceptionResponse,
    ValidationErrorResponse,
)

__all__ = [
    'HANDLERS',
    'FailedDependency',
    'Forbidden',
    'HttpException',
    'InternalError',
    'NotFound',
    'ScopusApiError',
    'Unauthorized',
    'UnprocessableContent',
    'BaseExceptionResponse',
    'PydanticValidationExceptionResponse',
    'ValidationErrorResponse',
]
