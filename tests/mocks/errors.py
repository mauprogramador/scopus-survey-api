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

from src.core.config.scopus import QUOTA_ERROR_CODE, RATE_LIMIT_ERROR_CODE
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import HTTPError, ScopusAPIError


HTTP_ERROR = HTTPError(
    HTTPStatus.BAD_REQUEST, ExcMsg.INTERNAL_ERROR, ValueError("any")
)

SCOPUS_API_ERROR = ScopusAPIError(
    HTTPStatus.INTERNAL_SERVER_ERROR,
    {"status": "any"},
    {"code": "ANY", "text": "any"},
    {"any": "any"},
)
SCOPUS_API_QUOTA_ERROR = ScopusAPIError(
    HTTPStatus.TOO_MANY_REQUESTS,
    {"status": "any"},
    {"code": QUOTA_ERROR_CODE, "text": "any"},
    {"any": "any"},
)
SCOPUS_API_RATE_ERROR = ScopusAPIError(
    HTTPStatus.TOO_MANY_REQUESTS,
    {"status": "any"},
    {"code": RATE_LIMIT_ERROR_CODE, "text": "any"},
    {"any": "any"},
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

TASKS_CANCELLED_ERROR = [
    None,
    None,
    asyncio.CancelledError("any"),
    None,
    None,
    None,
]

TASKS_HTTP_ERROR = [
    None,
    None,
    HTTP_ERROR,
    None,
    None,
    None,
]

TASKS_COMMON_ERROR = [
    None,
    None,
    PYDANTIC_VALIDATION_ERROR,
    None,
    None,
    None,
]
