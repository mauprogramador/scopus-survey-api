from http import HTTPStatus
from json import dumps

from fastapi import Request, FastAPI
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic_core import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from app.adapters.presenters.exception_json import ExceptionJSON
from app.core.common.messages import (
    PYDANTIC_ERROR,
    REQUEST_ERROR,
    RESPONSE_ERROR,
    UNEXPECTED_ERROR,
)
from app.core.config.config import LOG
from app.core.config.scopus import NULL
from app.core.domain.exceptions import ApplicationError
from app.core.domain.http_exceptions import HTTPException
from app.core.domain.exceptions import InterruptError
from app.utils.signal_handler import ShutdownSignalHandler


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling all exceptions"""

    __LIVERELOAD_ROUTE = "/livereload"

    def __init__(self, app: FastAPI):
        """Middleware for handling all exceptions"""
        super().__init__(app)
        self.__shutdown = ShutdownSignalHandler(for_async=True)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> ExceptionJSON | Response:

        try:
            response = await call_next(request)

            if self.__shutdown.event.is_set():
                raise InterruptError()

        except ApplicationError as exc:
            LOG.error(exc.message)
            response = ExceptionJSON(
                request, exc.code, exc.message, exc.errors
            )

        except HTTPException as exc:
            LOG.error(exc.message)
            response = ExceptionJSON(request, exc.code, exc.message)

        except FastAPIHTTPException as exc:
            if not exc.detail.isalnum():
                exc.detail = dumps(exc.detail)
            LOG.error(exc.detail)
            response = ExceptionJSON(request, exc.status_code, exc.detail)

        except StarletteHTTPException as exc:
            # if not request.url.path.count(self.__LIVERELOAD_ROUTE):
            LOG.error(exc.detail)
            response = ExceptionJSON(request, exc.status_code, exc.detail)

        except RequestValidationError as exc:
            first_error: dict = exc.errors()[0]
            message = REQUEST_ERROR.format(first_error.get("msg", NULL))

            LOG.error(message)
            LOG.exception(exc)

            response = ExceptionJSON(
                request,
                HTTPStatus.UNPROCESSABLE_ENTITY,
                message,
                exc.errors(),
            )

        except ResponseValidationError as exc:
            first_error: dict = exc.errors()[0]
            message = RESPONSE_ERROR.format(first_error.get("msg", NULL))

            LOG.error(message)
            LOG.exception(exc)

            response = ExceptionJSON(
                request,
                HTTPStatus.INTERNAL_SERVER_ERROR,
                message,
                exc.errors(),
            )

        except ValidationError as exc:
            message = PYDANTIC_ERROR.format(exc.error_count(), exc.title)

            LOG.error(message)
            LOG.exception(exc)

            response = ExceptionJSON(
                request,
                HTTPStatus.INTERNAL_SERVER_ERROR,
                message,
                exc.errors(),
            )

        except Exception as exc:  # pylint: disable=W0718
            message = exc.args[0] if exc.args[0] else UNEXPECTED_ERROR

            LOG.error(message)
            LOG.exception(exc)

            response = ExceptionJSON(
                request,
                HTTPStatus.INTERNAL_SERVER_ERROR,
                UNEXPECTED_ERROR.format(repr(exc)),
            )

        return response
