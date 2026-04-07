import fastapi
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response as StarletteResponse


class ProxyForwardedHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for mapping the scheme and host when forwarded."""

    _FORWARDED_PROTO = "x-forwarded-proto"
    _FORWARDED_HOST = "x-forwarded-host"

    def __init__(self, app: fastapi.FastAPI):
        """Middleware for mapping the scheme and host when forwarded."""
        super().__init__(app)

    async def dispatch(
        self, request: fastapi.Request, call_next: RequestResponseEndpoint
    ) -> StarletteResponse:

        proto = request.headers.get(self._FORWARDED_PROTO)
        host = request.headers.get(self._FORWARDED_HOST)

        if proto:
            request.scope["scheme"] = proto

        if host:
            port = 443 if proto == "https" else 80
            server = (host, port)

            headers = [
                (b"host", host.encode()) if name == b"host" else (name, value)
                for name, value in request.scope["headers"]
            ]

            request.scope["server"] = server
            request.scope["headers"] = headers

        response = await call_next(request)
        return response
