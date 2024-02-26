import pytest

from tests.data import mocks
from tests.data.request import app_request


@pytest.mark.asyncio
async def test_missing_api_key():
    response = await app_request(mocks.SEARCH_ARTICLES_URL)
    assert response.status_code == 403
    assert not response.json()['success']
    assert response.json()['message'] == mocks.MISSING_API_KEY


@pytest.mark.asyncio
async def test_short_invalid_api_key():
    response = await app_request(f'{mocks.API_KEY_URL}123')
    assert response.status_code == 400
    assert not response.json()['success']
    assert response.json()['message'] == mocks.VALIDATION_ERROR
    assert response.json()['detail'][0]['msg'] == mocks.INVALID_SHORT_VALUE


@pytest.mark.asyncio
async def test_long_invalid_api_key():
    key = 'be8be960662e54c8fd1e5132dd56cece0d852709'
    response = await app_request(f'{mocks.API_KEY_URL}{key}')
    assert response.status_code == 400
    assert not response.json()['success']
    assert response.json()['message'] == mocks.VALIDATION_ERROR
    assert response.json()['detail'][0]['msg'] == mocks.INVALID_LONG_VALUE


@pytest.mark.asyncio
async def test_value_invalid_api_key():
    key = 'b7@56!b$d5cf@3f!sH%3P3*d2db$5c@e'
    response = await app_request(f'{mocks.API_KEY_URL}{key}')
    assert response.status_code == 400
    assert not response.json()['success']
    assert response.json()['message'] == mocks.VALIDATION_ERROR
    assert response.json()['detail'][0]['msg'] == mocks.INVALID_PATTERN


@pytest.mark.asyncio
async def test_missing_keywords():
    response = await app_request(f'{mocks.API_KEY_URL}{mocks.API_KEY}')
    assert response.status_code == 422
    assert not response.json()['success']
    assert response.json()['message'] == mocks.MISSING_KEYWORDS


@pytest.mark.asyncio
async def test_blank_missing_keywords():
    response = await app_request(mocks.KEYWORDS_URL)
    assert response.status_code == 422
    assert not response.json()['success']
    assert response.json()['message'] == mocks.MISSING_KEYWORDS


@pytest.mark.asyncio
async def test_short_invalid_keywords():
    response = await app_request(f'{mocks.KEYWORDS_URL}1,2')
    assert response.status_code == 422
    assert not response.json()['success']
    assert response.json()['message'] == mocks.INVALID_KEYWORD


@pytest.mark.asyncio
async def test_long_invalid_keywords():
    keyword = 'a' * 121
    response = await app_request(f'{mocks.KEYWORDS_URL}key,{keyword}')
    assert response.status_code == 422
    assert not response.json()['success']
    assert response.json()['message'] == mocks.INVALID_KEYWORD


@pytest.mark.asyncio
async def test_value_invalid_keywords():
    keyword = 'b7@56!b$d cf@3f!sH%3P3*d_db$5ce'
    response = await app_request(f'{mocks.KEYWORDS_URL}key,{keyword}')
    assert response.status_code == 422
    assert not response.json()['success']
    assert response.json()['message'] == mocks.INVALID_KEYWORD


@pytest.mark.asyncio
async def test_invalid_minimum_length_keywords():
    response = await app_request(f'{mocks.KEYWORDS_URL}key')
    assert response.status_code == 422
    assert not response.json()['success']
    assert response.json()['message'] == mocks.INVALID_MINIMUM_LENGTH_KEYWORDS
