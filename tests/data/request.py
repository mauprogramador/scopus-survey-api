from httpx import AsyncClient, Response

from app.core.config import TOKEN
from app.main import app


async def app_request(url: str, headers: dict | None = None) -> Response:
    headers = {'X-access-token': TOKEN} if not headers else headers
    async with AsyncClient(app=app) as client:
        response = await client.get(url, headers=headers, timeout=15)
    return response
