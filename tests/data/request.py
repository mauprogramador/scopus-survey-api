from httpx import AsyncClient, Response

from app.core.config.config import TOKEN
from app.framework.fastapi.main import app


async def app_request(url: str, headers: dict | None = None) -> Response:
    headers = headers or {"X-access-token": TOKEN}
    async with AsyncClient(app=app) as client:
        response = await client.get(url, headers=headers, timeout=15)
    return response
