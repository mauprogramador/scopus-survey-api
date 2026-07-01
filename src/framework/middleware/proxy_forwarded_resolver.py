from fastapi import FastAPI
from fastapi.requests import Request as FastAPIRequest
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response as StarletteResponse


class ProxyForwardedResolverMiddleware(BaseHTTPMiddleware):
    """Middleware for mapping the scheme and host when forwarded"""

    def __init__(self, app: FastAPI):
        """Middleware for mapping the scheme and host when forwarded"""
        super().__init__(app)

    async def dispatch(
        self, request: FastAPIRequest, call_next: RequestResponseEndpoint
    ) -> StarletteResponse:

        proto = request.headers.get("x-forwarded-proto")
        host = request.headers.get("x-forwarded-host")

        if proto:
            request.scope["scheme"] = proto

        if host:
            port = 443 if proto == "https" else 80  # RFC TCP Standard
            server = (host, port)

            headers = [
                (b"host", host.encode()) if name == b"host" else (name, value)
                for name, value in request.scope["headers"]
            ]

            request.scope["server"] = server
            request.scope["headers"] = headers

        res = await call_next(request)
        return res
