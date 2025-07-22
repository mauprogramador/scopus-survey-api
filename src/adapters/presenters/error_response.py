from datetime import datetime
from http import HTTPStatus
from json import dumps

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from src.core.common.error_messages import SERIALIZE_ERROR
from src.core.common.types import Errors, Json
from src.core.config.config import ENV, LOG


class ErrorResponse(BaseModel):
    """JSON error response"""

    success: bool = False
    status_code: int
    status: str
    message: str
    timestamp: str = datetime.now().isoformat()
    request: Json
    errors: Errors = None

    @field_validator("request", mode="before")
    @classmethod
    def get_request_data(cls, request: Request) -> Json:
        return {
            "url": request.url.path,
            "host": request.client.host if request.client else ENV.host,
            "port": request.client.port if request.client else ENV.port,
            "method": request.method,
            "headers": request.headers.items(),
        }


class ErrorJSON(JSONResponse):
    """Error JSON representation response"""

    def __init__(
        self,
        request: Request,
        status_code: int,
        message: str,
        errors: Errors = None,
    ) -> None:
        """Error JSON representation response"""

        if errors is not None:
            try:
                dumps(errors)
            except Exception as exc:  # pylint: disable=W0718
                LOG.error(message, exc)
                LOG.exception(exc)

                message = SERIALIZE_ERROR
                errors = jsonable_encoder(errors)

                if not isinstance(errors, dict):
                    errors = {"serialize_error": errors}

        content = ErrorResponse(
            success=False,
            status_code=status_code,
            status=HTTPStatus(status_code).phrase,
            message=message,
            request=request,
            errors=errors,
        )

        super().__init__(content.model_dump(), status_code)
