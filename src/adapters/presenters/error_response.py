from datetime import datetime
from http import HTTPStatus
from json import dumps

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from src.core.common.error_messages import SERIALIZE_ERROR
from src.core.common.types import Json
from src.core.config.config import ENV, LOG
from src.core.domain.http_exceptions import HTTPError


class ErrorResponse(BaseModel):
    """JSON error response"""

    success: bool = False
    status_code: int
    status: str
    message: str
    timestamp: str = datetime.now().isoformat()
    request: Json
    errors: list[Json] | None = None

    @field_validator("request", mode="before")
    @classmethod
    def get_request_data(cls, data: Request | Json) -> Json:
        if isinstance(data, Request):
            return {
                "url": data.url.path,
                "host": data.client.host if data.client else ENV.host,
                "port": data.client.port if data.client else ENV.port,
                "method": data.method,
                "headers": data.headers.items(),
            }
        return data


class ErrorJSON(JSONResponse):
    """Error JSON representation response"""

    def __init__(
        self,
        request: Request,
        status_code: int,
        message: str,
        errors: list[Json] | Json | None = None,
    ) -> None:
        """Error JSON representation response"""

        if errors is not None:
            if isinstance(errors, dict):
                errors = [errors]

            try:
                dumps(errors)
            except (TypeError, ValueError) as exc:
                LOG.error(message, exc)
                LOG.exception(exc)

                message = SERIALIZE_ERROR
                errors: list[Json] = jsonable_encoder(errors)

                error = HTTPError.get_error_details(exc)[0]
                errors.append(error)

        error_response = ErrorResponse(
            success=False,
            status_code=status_code,
            status=HTTPStatus(status_code).phrase,
            message=message,
            request=request,
            errors=errors,
        )

        super().__init__(error_response.model_dump(), status_code)
