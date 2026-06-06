import re
import time
import uuid
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.requests import Request as FastAPIRequest
from fastapi.responses import HTMLResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
    _StreamingResponse,
)
from starlette.responses import Response as StarletteResponse

from src.adapters.presenters.json_response import ErrorJSON
from src.adapters.presenters.template_response import TemplateResponse
from src.core.config.config import (
    HEADERS,
    RATELIMIT_POLICY,
    SERVER,
    TRACE_ID_CTX,
)
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import InternalError
from src.framework.middleware.exception_handler import custom_http_error
from src.utils import logger


# e.g. /v2/scopus-survey/api
_API_ROUTES_PATTERN = re.compile(
    r"^\/v2\/scopus-survey\/api\/(combination|survey|csv)"
)


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
        self, request: FastAPIRequest, call_next: RequestResponseEndpoint
    ) -> StarletteResponse | ErrorJSON | HTMLResponse:
        token = TRACE_ID_CTX.set(str(uuid.uuid4()))
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            trace_id = TRACE_ID_CTX.get()

        except Exception as exc:  # pylint: disable=W0718
            trace_id = TRACE_ID_CTX.get()
            exc = InternalError(ExcMsg.UNEXPECTED_ERROR, exc)
            response = await custom_http_error(request, exc)

        finally:
            TRACE_ID_CTX.reset(token)

        process_time = time.perf_counter() - start_time
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
        if is_error and not _API_ROUTES_PATTERN.match(request.url.path):

            if isinstance(response, _StreamingResponse):
                chunks = [chunk async for chunk in response.body_iterator]
                setattr(response, "body", b"".join(chunks))

            return TemplateResponse.not_found_template(request, response)

        return response
