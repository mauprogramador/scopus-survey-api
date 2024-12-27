from http import HTTPStatus
from time import perf_counter

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
from app.utils.signal_handler import ShutdownSignalHandler


class TraceExceptionControl(BaseHTTPMiddleware):
    """Middleware for handling request tracing and exceptions"""

    __PROCESS_TIME = "X-Process-Time"

    def __init__(self, app: FastAPI):
        """Middleware for handling request tracing and exceptions"""
        super().__init__(app)
        self.__handler = ShutdownSignalHandler(True)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> ExceptionJSON | Response:

        start_time = perf_counter()
        try:
            response = await call_next(request)

        except InterruptError as exc:
            LOG.exception(exc)

            response = ExceptionJSON(exc.code, exc.message, exc.errors)

        except Exception as exc:  # pylint: disable=W0718
            LOG.exception(exc)
            message = UNEXPECTED_ERROR.format(repr(exc))

            response = ExceptionJSON(
                request, HTTPStatus.INTERNAL_SERVER_ERROR, message
            )

        if self.__handler.event.is_set():
            error = InterruptError()
            LOG.exception(error)

            response = ExceptionJSON(request, error.code, error.message)

        process_time = perf_counter() - start_time
        response.headers[self.__PROCESS_TIME] = f"{process_time:.2f}s"

        LOG.trace(request, response.status_code, process_time)

        return response
