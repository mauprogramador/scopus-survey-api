from http import HTTPStatus
from re import match
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response

from app.adapters.helpers.template_builder import TemplateBuilder
from app.adapters.presenters.exception_json import ExceptionJSON
from app.core.common.patterns import LANG_ROUTES, SURVEY_ROUTE
from app.core.config.config import LOG
from app.core.domain.exceptions import InterruptError
from app.utils.signal_handler import ShutdownSignalHandler


class RedirectNotFoundRoutes(BaseHTTPMiddleware):
    """Middleware to redirect any request for routes not found"""

    def __init__(self, app: FastAPI):
        """Middleware to redirect any request for routes not found"""
        super().__init__(app)
        self.__handler = ShutdownSignalHandler(True)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> HTMLResponse | ExceptionJSON | Response:

        url = request.url.path
        response = await call_next(request)

        if self.__handler.event.is_set():
            error = InterruptError()
            LOG.exception(error)

            response = ExceptionJSON(request, error.code, error.message)

        if response.status_code >= HTTPStatus.BAD_REQUEST:

            message = "Unexpected error"

            if response.status_code == HTTPStatus.NOT_FOUND and not match(
                SURVEY_ROUTE, url
            ):
                message = "Resource Not Found"
                LOG.error(message)

            elif (
                response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
                and match(LANG_ROUTES, url)
            ):
                message = "Language Not Supported"
                LOG.error(message)

            LOG.trace(request, response.status_code, 0)

            response = TemplateBuilder.not_found_template(
                request, response, message
            )

        return response
