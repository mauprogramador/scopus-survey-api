from tempfile import TemporaryDirectory

import pytest
from pytest_mock import MockerFixture

from tests.data import mocks
from tests.data.request import app_request


@pytest.mark.asyncio
async def test_search_articles(mocker: MockerFixture):
    with TemporaryDirectory() as tmpdir:
        mocker.patch(
            mocks.SEARCH_ARTICLES, return_value=mocks.get_csv_file(tmpdir)
        )
        response = await app_request(mocks.URL)
        assert response.status_code == 200
        assert len(response.text)
        assert mocks.CSV_CONTENT_TYPE in response.headers.items()


@pytest.mark.asyncio
async def test_get_template():
    response = await app_request(mocks.BASE_URL)
    assert response.status_code == 200
    assert len(response.text)
    assert mocks.HTML_CONTENT_TYPE in response.headers.items()
