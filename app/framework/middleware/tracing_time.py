from time import perf_counter

from fastapi import FastAPI, Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response


from app.core.config.config import LOG
from app.utils.logging import Prefix


class TracingTimeMiddleware(BaseHTTPMiddleware):
    """Middleware for handling request tracing and process time"""

    __PROCESS_TIME = "X-Process-Time"

    def __init__(self, app: FastAPI):
        """Middleware for handling request tracing and process time"""
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:

        print(request.session)
        start_time = perf_counter()

        response = await call_next(request)

        process_time = perf_counter() - start_time
        response.headers[self.__PROCESS_TIME] = f"{process_time:.2f}s"

        LOG.trace(Prefix.TRACE, request, response.status_code, process_time)

        return response
