from http import HTTPStatus
from re import match
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
    _StreamingResponse,
)
from starlette.responses import Response

from src.adapters.presenters.json_response import ErrorJSON
from src.adapters.presenters.template_response import TemplateResponse
from src.core.common.patterns import API_ROUTES_PATTERN
from src.core.config.config import LOG, RATELIMIT_POLICY, TRACE_ID_CTX
from src.core.domain.http_exceptions import HTTPError


class FlowGuardingMonitorMiddleware(BaseHTTPMiddleware):
    """Middleware for tracing, process time and uncaught errors"""

    _RATELIMIT_POLICY = "X-RateLimit-Policy"
    _PROCESS_TIME = "X-Process-Time"
    _TRACE_ID = "X-Trace-ID"

    def __init__(self, app: FastAPI):
        """Middleware for tracing, process time and uncaught errors"""
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response | ErrorJSON | HTMLResponse:
        trace_id = str(uuid4())
        token = TRACE_ID_CTX.set(trace_id)
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

        finally:
            TRACE_ID_CTX.reset(token)

        process_time = perf_counter() - start_time
        response.headers[self._TRACE_ID] = trace_id
        response.headers[self._PROCESS_TIME] = f"{process_time:.2f}s"
        response.headers[self._RATELIMIT_POLICY] = RATELIMIT_POLICY

        LOG.trace(request, response.status_code, process_time)

        is_error = response.status_code >= HTTPStatus.BAD_REQUEST
        if is_error and not match(API_ROUTES_PATTERN, request.url.path):

            if isinstance(response, _StreamingResponse):
                chunks = [chunk async for chunk in response.body_iterator]
                setattr(response, "body", b"".join(chunks))

            return TemplateResponse.not_found_template(request, response)

        return response
