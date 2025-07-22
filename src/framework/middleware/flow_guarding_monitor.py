from http import HTTPStatus
from re import match
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response

from src.adapters.presenters.error_response import ErrorJSON
from src.adapters.presenters.html_response import TemplateBuilder
from src.core.common.patterns import API_ROUTES_PATTERN
from src.core.config.config import LOG
from src.core.domain.http_exceptions import HTTPError


class FlowGuardingMonitorMiddleware(BaseHTTPMiddleware):
    """Middleware for tracing, process time and uncaught errors"""

    __PROCESS_TIME = "X-Process-Time"

    def __init__(self, app: FastAPI):
        """Middleware for tracing, process time and uncaught errors"""
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response | ErrorJSON | HTMLResponse:
        start_time = perf_counter()

        try:
            response = await call_next(request)

        except Exception as exc:  # pylint: disable=W0718
            message = LOG.error_message(exc)

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

        LOG.trace(request, response.status_code, process_time)

        if response.status_code >= HTTPStatus.BAD_REQUEST and not match(
            API_ROUTES_PATTERN, request.url.path
        ):
            return TemplateBuilder.not_found_template(request, response)

        return response
