import pytest
from pytest_mock import MockerFixture

from app.adapters.gateway.api_config import ApiConfig
from app.adapters.gateway.scopus_api import ScopusApi
from tests.data import mocks
from tests.data.request import app_request
from tests.data.utils import assert_csv_response


@pytest.mark.asyncio
async def test_unit_search_articles_200(mocker: MockerFixture):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST, return_value=mocks.FAKE_RESPONSE_FOUND
    )
    assert ScopusApi().search_articles(mocks.FAKE_API_PARAMS)


@pytest.mark.asyncio
async def test_unit_search_articles_pagination(mocker: MockerFixture):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST, side_effect=mocks.FAKE_RESPONSE_PAGINATION
    )
    entry = ScopusApi().search_articles(mocks.FAKE_API_PARAMS)
    assert len(entry) == 2
    assert entry == [{'A': 'any'}, {'B': 'any'}]


@pytest.mark.asyncio
@pytest.mark.parametrize('code', ApiConfig.RESPONSES.keys())
async def test_search_articles_invalid_responses(
    mocker: MockerFixture, code: int
):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST,
        return_value=mocks.FAKE_HTTP_RESPONSES[code],
    )
    response = await app_request(mocks.URL)
    assert response.status_code == 422
    data = response.json()
    assert not data['success']
    assert data['message'] == mocks.INVALID_RESPONSE
    assert data['status'].startswith(f'{code}')
    assert data['detail'] == ApiConfig.RESPONSES[code]


@pytest.mark.asyncio
async def test_search_articles_404(mocker: MockerFixture):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST,
        return_value=mocks.FAKE_HTTP_RESPONSES[404],
    )
    response = await app_request(mocks.URL)
    assert response.status_code == 422
    data = response.json()
    assert not data['success']
    assert data['message'] == mocks.INVALID_RESPONSE
    assert data['status'].startswith('404')
    assert data['detail'] == 'null'


@pytest.mark.asyncio
async def test_search_articles_decoding_error(mocker: MockerFixture):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST,
        return_value=mocks.FAKE_RESPONSE_NO_CONTENT,
    )
    response = await app_request(mocks.URL)
    assert response.status_code == 500
    assert response.json() == mocks.DECODING_ERROR


@pytest.mark.asyncio
async def test_search_articles_empty_content(mocker: MockerFixture):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST,
        return_value=mocks.FAKE_RESPONSE_DECODING_200,
    )
    response = await app_request(mocks.URL)
    assert response.status_code == 424
    assert response.json() == mocks.INVALID_RESPONSE


@pytest.mark.asyncio
async def test_search_articles_not_found(mocker: MockerFixture):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST,
        return_value=mocks.FAKE_RESPONSE_NOT_FOUND,
    )
    response = await app_request(mocks.URL)
    assert response.status_code == 404
    assert response.json() == mocks.NOT_FOUND


@pytest.mark.asyncio
async def test_unit_scraping_article_200(mocker: MockerFixture):
    mocker.patch(mocks.HTTP_HELPER_REQUEST, return_value=mocks.FAKE_TEMPLATE)
    response = ScopusApi.scraping_article('SCOPUS:123')
    assert response[0] == ApiConfig.get_article_page_url('123')
    assert response[1]


@pytest.mark.asyncio
async def test_scraping_article_400(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_ARTICLES,
    )
    mocker.patch(mocks.RANGE, return_value=range(2, 3))
    mocker.patch(
        mocks.SESSION_SEND,
        return_value=mocks.FAKE_HTTP_RESPONSES[400],
    )
    response = await app_request(mocks.URL)
    assert_csv_response(response)


@pytest.mark.asyncio
async def test_scraping_empty_content(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_ARTICLES,
    )
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST,
        return_value=mocks.FAKE_RESPONSE_DECODING_200,
    )
    mocker.patch(mocks.RANGE, return_value=range(2, 3))
    response = await app_request(mocks.URL)
    assert_csv_response(response)
