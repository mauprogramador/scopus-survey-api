import asyncio
from http import HTTPStatus
from json import JSONDecodeError
from unittest.mock import MagicMock, Mock

import aiohttp
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic_core import InitErrorDetails, PydanticUndefined, ValidationError
from slowapi.errors import Limit, RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.adapters.exceptions import BaseHTTPError
from src.core.domain.types import ExcMsg
from src.infra.config.scopus import QUOTA_ERROR_CODE, RATE_LIMIT_ERROR_CODE
from src.infra.exceptions import APIResponseError


HTTP_ERROR = BaseHTTPError(
    HTTPStatus.BAD_REQUEST, ExcMsg.INTERNAL_ERROR, ValueError("any")
)

SCOPUS_API_ERROR = APIResponseError(
    HTTPStatus.INTERNAL_SERVER_ERROR,
    {"status": "any"},
    {"code": "ANY", "text": "any"},
)
SCOPUS_API_QUOTA_ERROR = APIResponseError(
    HTTPStatus.TOO_MANY_REQUESTS,
    {"status": "any"},
    {"code": QUOTA_ERROR_CODE, "text": "any"},
)
SCOPUS_API_RATE_ERROR = APIResponseError(
    HTTPStatus.TOO_MANY_REQUESTS,
    {"status": "any"},
    {"code": RATE_LIMIT_ERROR_CODE, "text": "any"},
)

STARLETTE_HTTP_EXCEPTION = StarletteHTTPException(
    HTTPStatus.INTERNAL_SERVER_ERROR, "any"
)
FASTAPI_HTTP_EXCEPTION = FastAPIHTTPException(
    HTTPStatus.INTERNAL_SERVER_ERROR, "any"
)

REQUEST_VALIDATION_ERROR = RequestValidationError([{"msg": "any"}])
RESPONSE_VALIDATION_ERROR = ResponseValidationError([{"msg": "any"}])

RESPONSE_VALIDATION_EXCEPTION_ERROR = ResponseValidationError(
    [{"msg": "any", "ctx": {"error": ValueError("any")}}]
)

PYDANTIC_VALIDATION_ERROR = ValidationError.from_exception_data(
    "any", [InitErrorDetails(type="missing", input="any")]
)
PYDANTIC_UNDEFINED_ERROR = ValidationError.from_exception_data(
    "any", [InitErrorDetails(type="missing", input=PydanticUndefined)]
)

RATE_LIMIT_ERROR = RateLimitExceeded(Mock(Limit, error_message="any"))

JSON_DECODE_ERROR = JSONDecodeError("any", "any", 0)

CONTENT_TYPE_ERROR = aiohttp.ContentTypeError(
    MagicMock(aiohttp.RequestInfo),
    MagicMock(tuple[aiohttp.ClientResponse, ...]),
    status=HTTPStatus.BAD_REQUEST,
    message="any",
)

# Unpacking inside the worker task: TaskGroup swallows it up
TASKS_CANCELLED_ERROR = [
    (None, None),
    (None, None),
    (None, None),
    asyncio.CancelledError("any"),
    (None, None),
    (None, None),
    (None, None),
]

TASKS_HTTP_ERROR = [
    (None, None),
    (None, None),
    HTTP_ERROR,
    None,
    None,
    None,
]

TASKS_COMMON_ERROR = [
    (None, None),
    (None, None),
    PYDANTIC_VALIDATION_ERROR,
    None,
    None,
    None,
]

COMMON_ERROR_EXC_GROUP = ExceptionGroup(
    "any", [KeyError("any"), KeyError("any")]
)

HTTP_ERROR_EXC_GROUP = ExceptionGroup("any", [HTTP_ERROR, HTTP_ERROR])

PYDANTIC_ERROR_EXC_GROUP = ExceptionGroup(
    "any",
    [PYDANTIC_VALIDATION_ERROR, PYDANTIC_VALIDATION_ERROR],
)

SCOPUS_API_ERROR_EXC_GROUP = ExceptionGroup(
    "any", [SCOPUS_API_ERROR, SCOPUS_API_ERROR]
)
