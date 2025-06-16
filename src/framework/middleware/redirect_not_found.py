from http import HTTPStatus
from re import match

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response

from src.adapters.presenters.error_response import ErrorJSON
from src.adapters.presenters.html_response import TemplateBuilder
from src.core.common.messages import UNEXPECTED_ERROR
from src.core.common.patterns import API_ROUTES_PATTERN
from src.core.config.config import LOG


class RedirectNotFoundMiddleware(BaseHTTPMiddleware):
    """Middleware to redirect any request for routes not found"""

    def __init__(self, app: FastAPI):
        """Middleware to redirect any request for routes not found"""
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> HTMLResponse | Response:

        url = request.url.path
        response = await call_next(request)

        error_status = response.status_code >= HTTPStatus.BAD_REQUEST

        if error_status and not match(API_ROUTES_PATTERN, url):
            LOG.error(UNEXPECTED_ERROR)

            response = ErrorJSON(
                request, response.status_code, UNEXPECTED_ERROR
            )
            return TemplateBuilder.not_found_template(request, response)

        return response
