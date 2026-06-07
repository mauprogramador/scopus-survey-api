from datetime import datetime, timezone
from http import HTTPStatus

from fastapi.requests import Request as FastAPIRequest
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticSerializationError, to_jsonable_python

from src.core.common.types import Json
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import get_error_details
from src.utils import logger


class BaseResponse(BaseModel):
    success: bool
    status_code: int
    status: str
    message: str
    timestamp: str = datetime.now(timezone.utc).isoformat(timespec="seconds")


class ErrorResponse(BaseResponse):
    request: dict[str, str]
    tracking_id: str
    errors: list[Json] | None = None


class SuccessResponse(BaseResponse):
    data: Json


class ErrorJSON(JSONResponse):
    """Builds JSON error response and validates errors"""

    def __init__(
        self,
        request: FastAPIRequest,
        status_code: int,
        message: str,
        tracking_id: str,
        errors: list[Json] | Json | None = None,
    ) -> None:
        """Builds JSON error response and validates errors"""

        if errors is not None:
            if isinstance(errors, dict):
                errors = [errors]

            try:
                errors = to_jsonable_python(errors, fallback=repr)
            except (TypeError, ValueError, PydanticSerializationError) as exc:
                logger.error(ExcMsg.SERIALIZE_ERROR)
                logger.exception(exc)

                errors = get_error_details(exc)
                serialize_error = {
                    "desc": ExcMsg.SERIALIZE_ERROR,
                    "raw_repr": repr(errors),
                }
                errors.append(serialize_error)

        error_response = ErrorResponse(
            success=False,
            status_code=status_code,
            status=HTTPStatus(status_code).phrase,
            message=message,
            request={
                "path": request.url.path,
                "method": request.method,
            },
            tracking_id=tracking_id,
            errors=errors,
        )

        super().__init__(error_response.model_dump(), status_code)


class SuccessJSON(JSONResponse):
    """Builds JSON success response"""

    def __init__(
        self, data: Json, message: str, headers: dict[str, str]
    ) -> None:
        """Builds JSON success response"""

        success_response = SuccessResponse(
            success=True,
            status_code=HTTPStatus.OK,
            status=HTTPStatus.OK.phrase,
            message=message,
            data=data,
        )
        super().__init__(success_response.model_dump(), HTTPStatus.OK, headers)
