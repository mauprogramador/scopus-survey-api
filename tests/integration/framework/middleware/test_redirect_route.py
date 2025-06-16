import pytest

from tests.helpers.utils import app_request


@pytest.mark.asyncio
async def test_redirect():
    response = await app_request("/any/undefined/route")

    assert response.status_code == 307
    assert response.is_redirect and response.has_redirect_location
