import uuid
from http import HTTPStatus

from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.requests import Request as FastAPIRequest
from pydantic_core import ValidationError
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.adapters.presenters.json_response import ErrorJSON
from src.core.domain.enums import ExcMsg
from src.core.domain.exceptions import (
    HTTPError,
    InternalError,
    ScopusAPIError,
    get_error_details,
)
from src.core.domain.types import Json
from src.infra.i18n.translations import translate_error
from src.infra.utils import logger


def _get_tracking_id(exc: Exception) -> str:
    return f"ERR:{type(exc).__name__}:{uuid.uuid4().hex}"


def common_error(request: FastAPIRequest, exc: Exception) -> ErrorJSON:
    tracking_id = _get_tracking_id(exc)
    details = [get_error_details(exc)]

    if isinstance(exc, ExceptionGroup):
        for exc_item in exc.exceptions:
            if isinstance(exc_item, ScopusAPIError):
                details.extend(exc_item.details)
            else:
                details.append(get_error_details(exc_item))

    logger.error(details[0]["message"], tracking_id)
    logger.exception(exc)

    exc = InternalError(ExcMsg.INTERNAL_ERROR, exc)  # for translation only

    return ErrorJSON(
        request,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        translate_error(request, exc),
        tracking_id,
        details,
    )


async def custom_http_error(
    request: FastAPIRequest, exc: HTTPError
) -> ErrorJSON:
    tracking_id = _get_tracking_id(exc)

    logger.error(exc.detail, tracking_id)
    logger.exception(exc)

    return ErrorJSON(
        request,
        exc.status_code,
        translate_error(request, exc),
        tracking_id,
        exc.details,
    )


async def scopus_api_error(
    request: FastAPIRequest, exc: ScopusAPIError
) -> ErrorJSON:
    tracking_id = _get_tracking_id(exc)

    logger.error(exc.message, tracking_id)
    logger.exception(exc)

    return ErrorJSON(
        request,
        exc.status_code,
        translate_error(request, exc),
        tracking_id,
        exc.details,
    )


async def starlette_http_exception(
    request: FastAPIRequest,
    exc: StarletteHTTPException | FastAPIHTTPException,
) -> ErrorJSON:
    tracking_id = _get_tracking_id(exc)

    details = get_error_details(exc)

    if not logger.noisy_route_access(request.url.path):
        logger.error(exc.detail, tracking_id)
        logger.exception(exc)

    return ErrorJSON(
        request,
        exc.status_code,
        translate_error(request, exc),
        tracking_id,
        details,
    )


async def fastapi_validation_error(
    request: FastAPIRequest,
    exc: RequestValidationError | ResponseValidationError,
) -> ErrorJSON:
    tracking_id = _get_tracking_id(exc)
    details = get_error_details(exc)

    validation_errors: list[Json] = exc.errors()
    message = validation_errors[0].get("msg", ExcMsg.INTERNAL_ERROR)

    details["message"] = message
    details["errors"] = validation_errors

    logger.error(message, tracking_id)
    logger.exception(exc)

    if isinstance(exc, RequestValidationError):
        status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    else:
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return ErrorJSON(
        request,
        status_code,
        translate_error(request, exc),
        tracking_id,
        details,
    )


async def pydantic_validation_error(
    request: FastAPIRequest, exc: ValidationError
) -> ErrorJSON:
    tracking_id = _get_tracking_id(exc)
    details = get_error_details(exc)

    logger.error(details["message"], tracking_id)
    logger.exception(exc)

    return ErrorJSON(
        request,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        translate_error(request, exc),
        tracking_id,
        details,
    )


async def rate_limit_error(
    request: FastAPIRequest, exc: RateLimitExceeded
) -> ErrorJSON:
    tracking_id = _get_tracking_id(exc)
    details = get_error_details(exc)

    details["error"] = {
        "status_code": exc.status_code,
        "resource": request.url.path,
        "rate": exc.detail,
    }
    details["message"] = ExcMsg.SLOWAPI_RATE_ERROR

    logger.error(ExcMsg.SLOWAPI_RATE_ERROR, tracking_id)
    logger.exception(exc)

    return ErrorJSON(
        request,
        HTTPStatus.TOO_MANY_REQUESTS,
        translate_error(request, exc),
        tracking_id,
        details,
    )


HANDLERS = {
    HTTPError: custom_http_error,
    ScopusAPIError: scopus_api_error,
    StarletteHTTPException: starlette_http_exception,
    FastAPIHTTPException: starlette_http_exception,
    RequestValidationError: fastapi_validation_error,
    ResponseValidationError: fastapi_validation_error,
    ValidationError: pydantic_validation_error,
    RateLimitExceeded: rate_limit_error,
}
