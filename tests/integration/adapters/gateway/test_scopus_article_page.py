import pytest
from pytest_mock import MockerFixture

from app.core.config.scopus import ABSTRACT_COLUMN, AUTHORS_COLUMN, NULL
from tests.helpers.utils import app_request, content_response
from tests.mocks import common as data
from tests.mocks import integration as mock
from tests.mocks.fixtures import REQUEST


@pytest.mark.asyncio
async def test_one_row(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ONE_ROW)
    response = await app_request(data.URL)
    content = content_response(response)
    assert response.status_code == 200
    assert response.content and content.shape == (1, 10)


@pytest.mark.asyncio
async def test_two_rows(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.TWO_ROWS)
    response = await app_request(data.URL)
    content = content_response(response)
    assert response.status_code == 200
    assert response.content and content.shape == (2, 10)


@pytest.mark.asyncio
async def test_more_rows(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.MORE_ROWS)
    response = await app_request(data.URL)
    content = content_response(response)
    assert response.status_code == 200
    assert response.content and content.shape == (7, 10)


@pytest.mark.asyncio
async def test_status_error(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ERROR_RESPONSE)
    response = await app_request(data.URL)
    content = content_response(response)

    assert response.status_code == 200
    assert response.content and content.shape == (1, 10)
    assert content.loc[0, AUTHORS_COLUMN] == NULL
    assert content.loc[0, ABSTRACT_COLUMN] == NULL


@pytest.mark.asyncio
async def test_empty_response(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.EMPTY_RESPONSE)
    response = await app_request(data.URL)
    content = content_response(response)

    assert response.status_code == 200
    assert response.content and content.shape == (1, 10)
    assert content.loc[0, AUTHORS_COLUMN] == NULL
    assert content.loc[0, ABSTRACT_COLUMN] == NULL


@pytest.mark.asyncio
async def test_exceptions(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.EXCEPT_RESPONSE)
    response = await app_request(data.URL)
    content = content_response(response)

    assert response.status_code == 200
    assert response.content and content.shape == (1, 10)
    assert content.loc[0, AUTHORS_COLUMN] == NULL
    assert content.loc[0, ABSTRACT_COLUMN] == NULL


@pytest.mark.asyncio
async def test_second_chance(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.SECOND_CHANCE_RESPONSE)
    response = await app_request(data.URL)
    content = content_response(response)

    assert response.status_code == 200
    assert response.content and content.shape == (1, 10)
    assert content.loc[0, ABSTRACT_COLUMN] != NULL
