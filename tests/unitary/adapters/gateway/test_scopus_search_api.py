from pytest import raises
from pytest_mock import MockerFixture

from src.core.common.messages import SEARCH_API_ERROR, VALIDATE_ERROR
from src.core.data.serializers import ScopusSearch
from src.core.domain.http_exceptions import (
    BadGateway,
    InternalError,
    NotFound,
    ScopusAPIError,
)
from tests.mocks import common as data
from tests.mocks import unitary as mock
from tests.mocks.fixtures import HANDLE, REQUEST, SEARCH_API

ONE_PAGE = ScopusSearch.model_validate(
    {
        "search-results": {
            "opensearch:totalResults": 24,
            "opensearch:itemsPerPage": 25,
            "entry": [
                {
                    "@_fa": "true",
                    "prism:url": "https://api.elsevier.com/scopus_id/0",
                    "dc:identifier": "SCOPUS_ID:0",
                }
            ],
        }
    }
)


def test_one_page(mocker: MockerFixture):
    mocker.patch(REQUEST)
    mocker.patch(HANDLE, return_value=ONE_PAGE)
    result = SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert result is not None and len(result) == 1
    assert result[0] == mock.RESULTS[0]


def test_two_pages(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.TWO_PAGES)
    result = SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert result is not None and len(result) == 2
    assert result == mock.RESULTS[:2]


def test_more_pages(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.MORE_PAGES)
    result = SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert result is not None and len(result) == 7
    assert result == mock.RESULTS


def test_quota_exceeded(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=mock.EXCEEDED_RESPONSE)
    with raises(ScopusAPIError) as exc:
        SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert exc.value.code == 502
    assert exc.value.message == SEARCH_API_ERROR


def test_scopus_api_error(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.ERROR_RESPONSES[500])
    with raises(ScopusAPIError) as exc:
        SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert exc.value.code == 502
    assert exc.value.message == SEARCH_API_ERROR


def test_empty_content(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.EMPTY_RESPONSE)
    with raises(BadGateway) as exc:
        SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert exc.value.status_code == 502
    assert exc.value.message == SEARCH_API_ERROR


def test_decoding_error(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.ANY_RESPONSE)
    with raises(InternalError) as exc:
        SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert exc.value.status_code == 500
    assert exc.value.message == DECODING_ERROR


def test_validate_error(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.VALIDATE_ERROR_RESPONSE)
    with raises(InternalError) as exc:
        SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert exc.value.status_code == 500
    assert exc.value.message == VALIDATE_ERROR


def test_not_found(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.NOT_FOUND)
    with raises(NotFound) as exc:
        SEARCH_API.search_articles(data.SEARCH_PARAMS)
    assert exc.value.status_code == 404
    assert exc.value.message == NOT_FOUND_ERROR
