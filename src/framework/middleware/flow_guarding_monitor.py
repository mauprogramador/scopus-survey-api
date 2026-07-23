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

from src.adapters.presenters.jinja_response import get_not_found_template
from src.adapters.presenters.json_response import ErrorJSON
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
            res = await call_next(request)
            trace_id = TRACE_ID_CTX.get()

        except Exception as exc:  # pylint: disable=W0718
            trace_id = TRACE_ID_CTX.get()
            exc = InternalError(ExcMsg.INTERNAL_ERROR, exc)
            res = await custom_http_error(request, exc)

        finally:
            TRACE_ID_CTX.reset(token)

        process_time = time.perf_counter() - start_time

        logger.trace(request, res.status_code, process_time)

        res.headers["X-Trace-ID"] = trace_id
        res.headers["X-Process-Time"] = str(process_time)

        res.headers.update(HEADERS)
        res.headers["X-RateLimit-Policy"] = RATELIMIT_POLICY
        res.headers.update(self._server)

        is_error = res.status_code >= HTTPStatus.BAD_REQUEST
        if is_error and not _API_ROUTES_PATTERN.match(request.url.path):

            if isinstance(res, _StreamingResponse):
                chunks = [chunk async for chunk in res.body_iterator]
                setattr(res, "body", b"".join(chunks))

            return get_not_found_template(request, res)

        return res
