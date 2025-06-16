from http import HTTPStatus
from unittest.mock import patch

from pytest import fixture, raises

from src.adapters.helpers.scopus_response import ScopusResponse
from src.core.common.messages import SCOPUS_API_ERROR, VALIDATE_ERROR
from src.core.data.enums import ScopusCode
from src.core.data.serializers import ScopusSearch
from src.core.domain.http_exceptions import (
    BadGateway,
    InternalError,
    ScopusAPIError,
)
from tests.conftest import assert_http_error
from tests.helpers.models import ScopusResponse as Mock


@fixture(scope="module", name="response")
def search_response():
    yield ScopusResponse(ScopusSearch, "any")


def test_scopus_response(response: ScopusResponse):
    model: ScopusSearch = response.validate(Mock())
    assert model.total_results == 156 and model.items_per_page == 25


def test_status_error(response: ScopusResponse):
    with raises(ScopusAPIError) as exc:
        response.validate(Mock(code=HTTPStatus.BAD_REQUEST))
    assert_http_error(exc, 502, SCOPUS_API_ERROR)


def test_too_many_requests(response: ScopusResponse):
    with raises(ScopusAPIError) as exc:
        response.validate(Mock(code=HTTPStatus.TOO_MANY_REQUESTS))
    assert_http_error(exc, 502, SCOPUS_API_ERROR)


def test_quota_exceeded(response: ScopusResponse):
    json = {"service-error": {"status": {"statusCode": ScopusCode.QUOTA}}}
    with raises(ScopusAPIError) as exc:
        response.validate(Mock(json, code=HTTPStatus.TOO_MANY_REQUESTS))
    assert_http_error(exc, 502, SCOPUS_API_ERROR)


def test_rate_limit_exceeded(response: ScopusResponse):
    json = {"error-response": {"error-code": ScopusCode.RATE_LIMIT}}
    with raises(ScopusAPIError) as exc:
        response.validate(Mock(json, code=HTTPStatus.TOO_MANY_REQUESTS))
    assert_http_error(exc, 502, SCOPUS_API_ERROR)


@patch.object(Mock, "text", None)
def test_not_text(response: ScopusResponse):
    with raises(BadGateway) as exc:
        response.validate(Mock())
    assert_http_error(exc, 502, "any", False)


def test_json_validate_error(response: ScopusResponse):
    with raises(InternalError) as exc:
        response.validate(Mock({"search-results": ""}))
    assert_http_error(exc, 500, VALIDATE_ERROR)

    with raises(InternalError) as exc:
        response.validate(Mock({"any": "any"}))
    assert_http_error(exc, 500, VALIDATE_ERROR)
