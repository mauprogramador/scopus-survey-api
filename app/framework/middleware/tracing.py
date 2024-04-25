from time import time
from traceback import print_exc

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from app.core.config import LOG


class TraceControl(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ):
        start_time = time()

        try:
            response = await call_next(request)

        except Exception as exception:
            LOG.exception(exception)
            print_exc()

            raise exception

        end_time = (time() - start_time) * 1000

        LOG.trace(request, response.status_code, end_time)

        return response
