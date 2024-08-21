from datetime import datetime
from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic_core import PydanticUndefined

from app.core.common.types import Errors


class ExceptionJSON(JSONResponse):
    """Generates JSON representation responses for exceptions"""

    __KEY = "input"

    def __init__(
        self, request: Request, code: int, message: str, errors: Errors = None
    ) -> None:
        """Generates JSON representation responses for exceptions"""
        errors = list(map(self.__filter, errors)) if errors else None
        data = {
            "success": False,
            "code": code,
            "message": message,
            "request": self.__request_data(request),
            "errors": errors,
            "timestamp": datetime.now().isoformat(),
        }
        super().__init__(jsonable_encoder(data), code)

    def __filter(self, item: dict[str, Any]) -> Any:
        if self.__KEY in item and item[self.__KEY] is PydanticUndefined:
            item[self.__KEY] = None
        return item

    def __request_data(self, request: Request) -> dict[str, Any]:
        return {
            "host": request.client.host if request.client else "127.0.0.1",
            "port": request.client.port if request.client else 8000,
            "method": request.method,
            "url": request.url.path,
            "headers": request.headers.items()
        }
