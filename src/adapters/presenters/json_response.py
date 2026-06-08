from datetime import datetime, timezone
from http import HTTPStatus

from fastapi.requests import Request as FastAPIRequest
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from pydantic_core import PydanticSerializationError, to_jsonable_python

from src.core.common.types import Json
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import get_error_details
from src.utils import logger


class BaseResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    success: bool
    status_code: int
    status: str
    message: str
    timestamp: str = datetime.now(timezone.utc).isoformat(timespec="seconds")


class ErrorResponse(BaseResponse):
    request: dict[str, str]
    tracking_id: str
    details: list[Json] | None = None


class SuccessResponse(BaseResponse):
    result: Json


class ErrorJSON(JSONResponse):
    """Builds JSON error response and validates details"""

    def __init__(
        self,
        request: FastAPIRequest,
        status_code: int,
        message: str,
        tracking_id: str,
        details: list[Json] | Json | None = None,
    ) -> None:
        """Builds JSON error response and validates details"""

        if details is not None:
            if isinstance(details, dict):
                details = [details]

            try:
                details = to_jsonable_python(details, fallback=repr)
            except (TypeError, ValueError, PydanticSerializationError) as exc:
                logger.error(ExcMsg.SERIALIZE_ERROR)
                logger.exception(exc)

                details = get_error_details(exc)
                serialize_detail = {
                    "desc": ExcMsg.SERIALIZE_ERROR,
                    "raw_repr": repr(details),
                }
                details.append(serialize_detail)

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
            details=details,
        )

        super().__init__(error_response.model_dump(), status_code)


class SuccessJSON(JSONResponse):
    """Builds JSON success response"""

    def __init__(
        self, result: Json, message: str, headers: dict[str, str]
    ) -> None:
        """Builds JSON success response"""

        success_response = SuccessResponse(
            success=True,
            status_code=HTTPStatus.OK,
            status=HTTPStatus.OK.phrase,
            message=message,
            result=result,
        )
        super().__init__(success_response.model_dump(), HTTPStatus.OK, headers)
