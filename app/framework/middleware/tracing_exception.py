from time import time

from fastapi import FastAPI, Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response

from app.adapters.presenters.exception_json import ExceptionJSON
from app.core.common.messages import UNEXPECTED_ERROR
from app.core.config.config import LOG
from app.core.domain.exceptions import InterruptError
from app.utils.signal_handler import SignalHandler


class TraceExceptionControl(BaseHTTPMiddleware):
    """Middleware for handling request tracing and exceptions"""

    def __init__(self, app: FastAPI):
        """Middleware for handling request tracing and exceptions"""
        super().__init__(app)
        self.__handler = SignalHandler(True)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> ExceptionJSON | Response:

        start_time = time()
        try:
            response = await call_next(request)

        except InterruptError as exc:
            LOG.trace(request, exc.code, start_time)
            LOG.exception(exc)

            return ExceptionJSON(exc.code, exc.message, exc.errors)

        except Exception as exc:  # pylint: disable=W0718
            LOG.trace(request, 500, start_time)
            LOG.exception(exc)
            message = UNEXPECTED_ERROR.format(repr(exc))

            return ExceptionJSON(request, 500, message)

        if self.__handler.event.is_set():
            error = InterruptError()
            LOG.trace(request, error.code, start_time)
            LOG.exception(error)

            return ExceptionJSON(request, error.code, error.message)

        LOG.trace(request, response.status_code, start_time)
        return response
