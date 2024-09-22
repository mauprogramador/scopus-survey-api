from pytest import raises
from pytest_mock import MockerFixture

from app.core.common.messages import (
    DECODING_ERROR,
    NOT_FOUND_ERROR,
    SEARCH_API_ERROR,
    VALIDATE_ERROR,
)
from app.core.data.serializers import ScopusResult
from app.core.domain.exceptions import ScopusAPIError
from app.framework.exceptions import BadGateway, InternalError, NotFound
from tests.mocks import common as data
from tests.mocks import unitary as mock
from tests.mocks.fixtures import REQUEST, SEARCH_API


def test_one_page(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=mock.ONE_PAGE[0])
    result = SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert result is not None and len(result) == 1
    assert result[0] == ScopusResult(**mock.ENTRIES[0])


def test_two_pages(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.TWO_PAGES)
    result = SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert result is not None and len(result) == 2
    assert result == [ScopusResult(**art) for art in mock.ENTRIES[:2]]


def test_more_pages(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.MORE_PAGES)
    result = SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert result is not None and len(result) == 7
    assert result == [ScopusResult(**art) for art in mock.ENTRIES]


def test_quota_exceeded(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=mock.EXCEEDED_RESPONSE)
    with raises(ScopusAPIError) as error:
        SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert error.value.code == 502
    assert error.value.message == SEARCH_API_ERROR


def test_scopus_api_error(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.ERROR_RESPONSES[500])
    with raises(ScopusAPIError) as error:
        SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert error.value.code == 502
    assert error.value.message == SEARCH_API_ERROR


def test_empty_content(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.EMPTY_RESPONSE)
    with raises(BadGateway) as error:
        SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert error.value.status_code == 502
    assert error.value.message == SEARCH_API_ERROR


def test_decoding_error(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.ANY_RESPONSE)
    with raises(InternalError) as error:
        SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert error.value.status_code == 500
    assert error.value.message == DECODING_ERROR


def test_validate_error(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.VALIDATE_ERROR_RESPONSE)
    with raises(InternalError) as error:
        SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert error.value.status_code == 500
    assert error.value.message == VALIDATE_ERROR


def test_not_found(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.NOT_FOUND)
    with raises(NotFound) as error:
        SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert error.value.status_code == 404
    assert error.value.message == NOT_FOUND_ERROR
