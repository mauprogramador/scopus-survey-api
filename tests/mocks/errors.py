from asyncio import CancelledError
from http import HTTPStatus
from json import JSONDecodeError
from typing import Tuple
from unittest.mock import MagicMock, Mock

from aiohttp import ClientResponse, ContentTypeError, RequestInfo
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic_core import InitErrorDetails, PydanticUndefined, ValidationError
from slowapi.errors import Limit, RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.domain.http_exceptions import HTTPError, ScopusAPIError


HTTP_ERROR = HTTPError(HTTPStatus.BAD_REQUEST, "any", ValueError("any"))

SCOPUS_API_ERROR = ScopusAPIError(
    HTTPStatus.INTERNAL_SERVER_ERROR, {"any": "any"}, "any"
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

CONTENT_TYPE_ERROR = ContentTypeError(
    MagicMock(RequestInfo),
    MagicMock(Tuple[ClientResponse, ...]),
    status=HTTPStatus.BAD_REQUEST,
    message="any",
)

MORE_CANCELLED = [None, None, CancelledError("any")]
