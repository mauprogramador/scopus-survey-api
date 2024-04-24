from time import time
from traceback import print_exc

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from app.utils.logger import Logger


class TraceControl(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ):
        start_time = time()

        try:
            response = await call_next(request)

        except Exception as exception:
            Logger.exception(exception)
            print_exc()

            raise exception

        end_time = (time() - start_time) * 1000

        Logger.trace(request, response, end_time)

        return response
