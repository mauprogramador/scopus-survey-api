import pytest

from tests.data import mocks
from tests.data.request import app_request


@pytest.mark.asyncio
async def test_missing_access_token():
    headers = {'X-a': 'a'}
    response = await app_request(mocks.URL, headers)
    assert response.status_code == 401
    assert not response.json()['success']
    assert response.json()['message'] == mocks.MISSING_ACCESS_TOKEN


@pytest.mark.asyncio
async def test_short_invalid_access_token():
    headers = {'X-Access-Token': '123'}
    response = await app_request(mocks.URL, headers)
    assert response.status_code == 400
    assert not response.json()['success']
    assert response.json()['message'] == mocks.VALIDATION_ERROR
    assert response.json()['detail'][0]['msg'] == mocks.INVALID_SHORT_VALUE


@pytest.mark.asyncio
async def test_long_invalid_access_token():
    headers = {'X-Access-Token': '7cac1b4fdf3adc9e07e8643ffab60e9e3a1'}
    response = await app_request(mocks.URL, headers)
    assert response.status_code == 400
    assert not response.json()['success']
    assert response.json()['message'] == mocks.VALIDATION_ERROR
    assert response.json()['detail'][0]['msg'] == mocks.INVALID_LONG_VALUE


@pytest.mark.asyncio
async def test_value_invalid_access_token():
    headers = {'X-Access-Token': 'b7@56!b$d5cf@3f!sH%3P3*d2db$5c@e'}
    response = await app_request(mocks.URL, headers)
    assert response.status_code == 400
    assert not response.json()['success']
    assert response.json()['message'] == mocks.VALIDATION_ERROR
    assert response.json()['detail'][0]['msg'] == mocks.INVALID_PATTERN


@pytest.mark.asyncio
async def test_invalid_access_token():
    headers = {'X-Access-Token': '6d29d9eeeeee043cef8a100c131a51ea'}
    response = await app_request(mocks.URL, headers)
    assert response.status_code == 401
    assert not response.json()['success']
    assert response.json()['message'] == mocks.INVALID_ACCESS_TOKEN
