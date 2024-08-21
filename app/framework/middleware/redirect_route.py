from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response

from app.adapters.presenters.exception_json import ExceptionJSON
from app.core.config.config import LOG
from app.core.domain.exceptions import InterruptError
from app.utils.signal_handler import SignalHandler


class RedirectNotFoundRoutes(BaseHTTPMiddleware):
    """Middleware to redirect any request for routes not found"""

    __MAIN_ROUTE = "/scopus-searcher/api"
    __RELOAD_ROUTE = '/livereload'

    def __init__(self, app: FastAPI):
        """Middleware to redirect any request for routes not found"""
        super().__init__(app)
        self.__handler = SignalHandler(True)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> RedirectResponse | ExceptionJSON | Response:

        response = await call_next(request)

        is_main_route = request.url.path.count(self.__MAIN_ROUTE)
        is_reload_route = request.url.path.count(self.__RELOAD_ROUTE)
        allowed_route = bool(is_main_route) or bool(is_reload_route)

        if response.status_code == 404 and not allowed_route:
            LOG.error("Route Not Found")
            # LOG.error("Route Not Found", False)
            return RedirectResponse(url=self.__MAIN_ROUTE)

        if self.__handler.event.is_set():
            error = InterruptError()
            LOG.exception(error)

            return ExceptionJSON(request, error.code, error.message)

        return response
