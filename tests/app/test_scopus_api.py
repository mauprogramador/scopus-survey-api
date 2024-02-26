import pytest
from pytest_mock import MockerFixture

from app.exceptions import ScopusApiError
from app.gateway.api_config import ApiConfig
from app.gateway.scopus_api import ScopusApi
from tests.data import mocks
from tests.data.request import app_request


@pytest.mark.asyncio
async def test_unit_search_articles_200(mocker: MockerFixture):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST, return_value=mocks.FAKE_SEARCH_ARTICLES_200
    )
    assert ScopusApi.search_articles(mocks.FAKE_API_PARAMS)


@pytest.mark.asyncio
@pytest.mark.parametrize('code', ApiConfig.RESPONSES.keys())
async def test_search_articles_invalid_responses(
    mocker: MockerFixture, code: int
):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST,
        return_value=mocks.FAKE_HTTP_HELPER_REQUEST[code],
    )
    response = await app_request(mocks.URL)
    assert response.status_code == 422
    data = ScopusApiError(**response.json())
    assert not data.success
    assert data.message == mocks.INVALID_RESPONSE
    assert data.status.startswith(f'{code}')
    assert data.detail == ApiConfig.RESPONSES[code]


@pytest.mark.asyncio
async def test_search_articles_404(mocker: MockerFixture):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST,
        return_value=mocks.FAKE_HTTP_HELPER_REQUEST[404],
    )
    response = await app_request(mocks.URL)
    assert response.status_code == 422
    data = ScopusApiError(**response.json())
    assert not data.success
    assert data.message == mocks.INVALID_RESPONSE
    assert data.status.startswith('404')
    assert data.detail == 'null'


@pytest.mark.asyncio
async def test_search_articles_decoding_error(mocker: MockerFixture):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST,
        return_value=mocks.FAKE_SEARCH_ARTICLES_DECODING_ERROR,
    )
    response = await app_request(mocks.URL)
    assert response.status_code == 500
    assert not response.json()['success']
    assert response.json()['message'] == mocks.DECODING_ERROR


@pytest.mark.asyncio
async def test_search_articles_empty_content(mocker: MockerFixture):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST,
        return_value=mocks.FAKE_SEARCH_ARTICLES_EMPTY_CONTENT,
    )
    response = await app_request(mocks.URL)
    assert response.status_code == 424
    assert not response.json()['success']
    assert response.json()['message'] == mocks.INVALID_RESPONSE


@pytest.mark.asyncio
async def test_search_articles_not_found(mocker: MockerFixture):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST,
        return_value=mocks.FAKE_SEARCH_ARTICLES_NOT_FOUND,
    )
    response = await app_request(mocks.URL)
    assert response.status_code == 404
    assert not response.json()['success']
    assert response.json()['message'] == mocks.NOT_FOUND


@pytest.mark.asyncio
async def test_unit_scraping_article_200(mocker: MockerFixture):
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST, return_value=mocks.FAKE_SCRAPING_ARTICLE_200
    )
    response = ScopusApi.scraping_article(mocks.FAKE_SCOPUS_ID)
    assert response[0] == ApiConfig.get_article_page_url(mocks.FAKE_ARTICLE_ID)
    assert len(response[1])


@pytest.mark.asyncio
async def test_scraping_article_400(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_SCOPUS_API_SEARCH_ARTICLES,
    )
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST,
        return_value=mocks.FAKE_HTTP_HELPER_REQUEST[400],
    )
    response = await app_request(mocks.URL)
    assert response.status_code == 424
    assert not response.json()['success']
    assert response.json()['message'] == mocks.INVALID_ARTICLE_PAGE


@pytest.mark.asyncio
async def test_scraping_empty_content(mocker: MockerFixture):
    mocker.patch(
        mocks.SCOPUS_API_SEARCH_ARTICLES,
        return_value=mocks.FAKE_SCOPUS_API_SEARCH_ARTICLES,
    )
    mocker.patch(
        mocks.HTTP_HELPER_REQUEST,
        return_value=mocks.FAKE_SCRAPING_ARTICLE_EMPTY_CONTENT,
    )
    response = await app_request(mocks.URL)
    assert response.status_code == 424
    assert not response.json()['success']
    assert response.json()['message'] == mocks.INVALID_ARTICLE_PAGE
