from http import HTTPStatus
from time import perf_counter

from fastapi import FastAPI, Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response

from src.adapters.presenters.error_response import ErrorJSON
from src.core.config.config import LOG
from src.core.domain.http_exceptions import HTTPError
from src.utils.formatters import get_error_message
from src.utils.logging import Prefix


class TracingTimeUncaughtErrorsMiddleware(BaseHTTPMiddleware):
    """Middleware for tracing, process time and uncaught errors"""

    __PROCESS_TIME = "X-Process-Time"

    def __init__(self, app: FastAPI):
        """Middleware for tracing, process time and uncaught errors"""
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response | ErrorJSON:
        start_time = perf_counter()

        try:
            response = await call_next(request)

        except Exception as exc:  # pylint: disable=W0718
            message = get_error_message(exc)

            LOG.error(message)
            LOG.exception(exc)

            response = ErrorJSON(
                request,
                HTTPStatus.INTERNAL_SERVER_ERROR,
                message,
                HTTPError.get_error_details(exc),
            )

        process_time = perf_counter() - start_time
        response.headers[self.__PROCESS_TIME] = f"{process_time:.2f}s"

        LOG.trace(Prefix.TRACE, request, response.status_code, process_time)

        return response
