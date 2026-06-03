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
from src.core.config.config import (
    HEADERS,
    RATELIMIT_POLICY,
    SERVER,
    TRACE_ID_CTX,
)
from src.core.domain.http_exceptions import HTTPError
from src.utils import logger


# e.g. /v2/scopus-survey/api
_API_ROUTES_PATTERN = r"^\/v2\/scopus-survey\/api\/(combination|survey|csv)"


class FlowGuardingMonitorMiddleware(BaseHTTPMiddleware):
    """Middleware for tracing, process time and uncaught errors"""

    _RATELIMIT_POLICY = "X-RateLimit-Policy"
    _PROCESS_TIME = "X-Process-Time"
    _TRACE_ID = "X-Trace-ID"
    _ONE_MINUTE = 60

    def __init__(self, app: FastAPI):
        """Middleware for tracing, process time and uncaught errors"""
        self._server = {"Server": SERVER.get()}
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response | ErrorJSON | HTMLResponse:
        token = TRACE_ID_CTX.set(str(uuid4()))
        start_time = perf_counter()

        try:
            response = await call_next(request)
            trace_id = TRACE_ID_CTX.get()

        except Exception as exc:  # pylint: disable=W0718
            trace_id = TRACE_ID_CTX.get()
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
        if process_time > self._ONE_MINUTE:
            minutes = process_time / self._ONE_MINUTE
            duration = f"{process_time:.2f}s ({minutes:.2f}m)"
        else:
            duration = f"{process_time:.2f}s"

        logger.trace(request, response.status_code, duration)

        response.headers[self._TRACE_ID] = trace_id
        response.headers[self._PROCESS_TIME] = duration

        response.headers.update(HEADERS)
        response.headers[self._RATELIMIT_POLICY] = RATELIMIT_POLICY
        response.headers.update(self._server)

        is_error = response.status_code >= HTTPStatus.BAD_REQUEST
        if is_error and not match(_API_ROUTES_PATTERN, request.url.path):

            if isinstance(response, _StreamingResponse):
                chunks = [chunk async for chunk in response.body_iterator]
                setattr(response, "body", b"".join(chunks))

            return TemplateResponse.not_found_template(request, response)

        return response
