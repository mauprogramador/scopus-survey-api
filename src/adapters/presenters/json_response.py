from datetime import datetime, timezone
from http import HTTPStatus

from fastapi.requests import Request as FastAPIRequest
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from pydantic_core import PydanticSerializationError, to_jsonable_python

from src.core.domain.enums import ExcMsg
from src.core.domain.exceptions import get_error_details
from src.core.domain.types import CombinationParams, Json, ScopusHeaders
from src.infra.utils import logger


class BaseResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    success: bool
    status_code: int
    status: str
    message: str
    timestamp: str = datetime.now(timezone.utc).isoformat(
        timespec="seconds"  # e.g. 2026-01-01T00:00:00Z
    )


class ErrorResponse(BaseResponse):
    request: dict[str, str]
    tracking_id: str
    details: list[Json] | None = None


class SuccessResponse(BaseResponse):
    result: Json


class ErrorJSON(JSONResponse):
    """Builds JSON error response and validates details"""

    def __init__(  # pylint: disable=R0913,R0917
        self,
        request: FastAPIRequest,
        status_code: int,
        message: str,
        tracking_id: str,
        details: Json | list[Json] | None = None,
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

                serialize_detail = get_error_details(exc)
                serialize_detail["original_error"] = {
                    "message": message,
                    "status_code": status_code,
                    "raw_details": repr(details),
                }

                message = ExcMsg.SERIALIZE_ERROR
                status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                details = [serialize_detail]

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


def json_response(
    params: CombinationParams,
    quota_headers: ScopusHeaders,
    results: list[Json],
) -> SuccessJSON:
    headers = {
        "X-API-Key": params.api_key,
        "X-Keywords": "; ".join(params.keywords),
        "X-Search-Limit": str(quota_headers.limit),
        "X-Search-Remaining": str(quota_headers.remaining),
        "X-Search-Reset": str(quota_headers.reset),
    }
    return SuccessJSON(
        result={"combinations": results},
        message="Combination totals survey successfully",
        headers=headers,
    )
