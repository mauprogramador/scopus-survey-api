from http import HTTPStatus

from pytest import raises
from pytest_mock import MockerFixture

from src.core.common.messages import ABSTRACT_API_ERROR, VALIDATE_ERROR
from src.core.domain.http_exceptions import (
    BadGateway,
    InternalError,
    ScopusAPIError,
)
from tests.mocks import common as data
from tests.mocks import unitary as mock
from tests.mocks.fixtures import ABSTRACT_API, REQUEST


def test_one_abstract(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=mock.ONE_ABSTRACT)
    result = ABSTRACT_API.retrieve_abstracts(data.API_KEY, mock.ONE_ENTRY)
    assert result is not None and result.shape == (1, 11)
    assert result.equals(mock.ARTICLES.iloc[0:1])


def test_two_abstract(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=mock.ONE_ABSTRACT)
    result = ABSTRACT_API.retrieve_abstracts(data.API_KEY, mock.TWO_ENTRIES)
    assert result is not None and result.shape == (2, 11)
    assert result.equals(mock.ARTICLES.iloc[0:2])


def test_more_abstracts(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=mock.ONE_ABSTRACT)
    result = ABSTRACT_API.retrieve_abstracts(data.API_KEY, mock.MORE_ENTRIES)
    assert result is not None and result.shape == (7, 11)
    assert result.equals(mock.ARTICLES)


def test_quota_exceeded(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=mock.EXCEEDED_RESPONSE)
    with raises(ScopusAPIError) as exc:
        ABSTRACT_API.retrieve_abstracts(data.API_KEY, mock.ONE_ENTRY)
    assert_error(exc, HTTPStatus.BAD_GATEWAY, ABSTRACT_API_ERROR)


def test_scopus_api_error(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.ERROR_RESPONSES[500])
    with raises(ScopusAPIError) as exc:
        ABSTRACT_API.retrieve_abstracts(data.API_KEY, mock.ONE_ENTRY)
    assert exc.value.code == 502
    assert exc.value.message == ABSTRACT_API_ERROR


def test_empty_content(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.EMPTY_RESPONSE)
    with raises(BadGateway) as exc:
        ABSTRACT_API.retrieve_abstracts(data.API_KEY, mock.ONE_ENTRY)
    assert exc.value.status_code == 502
    assert exc.value.message == ABSTRACT_API_ERROR


def test_decoding_error(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.ANY_RESPONSE)
    with raises(InternalError) as exc:
        ABSTRACT_API.retrieve_abstracts(data.API_KEY, mock.ONE_ENTRY)
    assert exc.value.status_code == 500
    assert exc.value.message == DECODING_ERROR


def test_validate_error(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.VALIDATE_ERROR_RESPONSE)
    with raises(InternalError) as exc:
        ABSTRACT_API.retrieve_abstracts(data.API_KEY, mock.ONE_ENTRY)
    assert exc.value.status_code == 500
    assert exc.value.message == VALIDATE_ERROR
