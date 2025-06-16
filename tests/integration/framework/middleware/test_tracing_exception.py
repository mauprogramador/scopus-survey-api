import pytest
from pytest_mock import MockerFixture

from src.adapters.presenters.error_response import ErrorResponse
from tests.helpers.utils import app_request
from tests.mocks import fixtures as fix
from tests.mocks.common import URL


@pytest.mark.asyncio
async def test_exception(mocker: MockerFixture):
    error = RuntimeError("any")
    mocker.patch(fix.SEARCH_ARTICLES, side_effect=error)
    response = await app_request(URL)
    exc_response = ErrorResponse.model_validate(response.json())

    assert response.status_code == 500
    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == UNEXPECTED_ERROR.format(repr(error))
    assert not exc_response.errors
