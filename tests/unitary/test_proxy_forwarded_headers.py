# mypy: disable-error-code="index"
from unittest.mock import AsyncMock

import fastapi
from pytest import fixture, mark
from starlette.middleware.base import RequestResponseEndpoint
from starlette.testclient import TestClient
from starlette.types import Scope as StarletteScope

from src.framework.middleware.proxy_forwarded_resolver import (
    ProxyForwardedResolverMiddleware,
)
from tests.mocks.raw import HTTP_200


@mark.asyncio
async def test_success_headers():
    scope: StarletteScope = {  # type: ignore
        "type": "http",
        "method": "GET",
        "scheme": "http",
        "server": ("127.0.0.1", 8000),
        "headers": [
            (b"host", b"localhost:8000"),
            (b"x-forwarded-proto", b"https"),
            (b"x-forwarded-host", b"any.com.br"),
        ],
    }

    request = fastapi.Request(scope)
    call_next = AsyncMock(RequestResponseEndpoint)
    middleware = ProxyForwardedResolverMiddleware(None)

    await middleware.dispatch(request, call_next)
    call_next.assert_called_once_with(request)

    assert request.scope["scheme"] == "https"
    assert request.scope["server"][0] == "any.com.br"
    assert request.scope["headers"][0] == (b"host", b"any.com.br")


@fixture(scope="module", name="client")
def sub_app_test_client():
    app = fastapi.FastAPI()
    app.add_middleware(ProxyForwardedResolverMiddleware)

    @app.get("/test")
    def test_url_for_route(request: fastapi.Request):
        return {"url": str(request.url_for("test_url_for_route"))}

    client = TestClient(app)
    return client


def test_proxy_headers_updates_url_for(client: TestClient):

    headers = {
        "X-Forwarded-Proto": "https",
        "X-Forwarded-Host": "any.com.br",
    }

    res = client.get("/test", headers=headers)
    assert res.status_code == HTTP_200
    assert res.json()["url"] == "https://any.com.br/test"


def test_no_proxy_headers_uses_default(client: TestClient):
    res = client.get("/test")

    assert res.status_code == HTTP_200
    assert res.json()["url"].startswith("http://testserver")
