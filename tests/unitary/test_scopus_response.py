from pydantic_core import ValidationError
from pytest import raises

from src.adapters.helpers.scopus_response import ScopusResponse
from src.core.common.types import ResponseBundle
from src.core.config.scopus import QUOTA_ERROR_CODE, RATE_LIMIT_ERROR_CODE
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import InternalError, ScopusAPIError
from tests.conftest import assert_http_error
from tests.mocks.helpers import fqn
from tests.mocks.raw import (
    HTTP_200,
    HTTP_400,
    HTTP_429,
    HTTP_500,
    HTTP_502,
    RAW_ERROR_RESPONSE_RATE_LIMIT,
    RAW_HEADERS_OK,
    RAW_SEARCH_OK,
    RAW_SERVICE_ERROR_INVALID_INPUT,
    RAW_SERVICE_ERROR_QUOTA,
)


def test_scopus_response():
    res = ResponseBundle(HTTP_200, RAW_HEADERS_OK, RAW_SEARCH_OK)
    model = ScopusResponse.validate_search(res)
    assert model.total_results == 1 and model.items_per_page == 1
    assert len(model.entry) == 1


def test_status_error():
    headers = {"X-ELS-Status": "INVALID_INPUT"}
    res = ResponseBundle(HTTP_400, headers, RAW_SERVICE_ERROR_INVALID_INPUT)
    with raises(ScopusAPIError) as info:
        ScopusResponse.validate_search(res)
    assert_http_error(info, HTTP_502, "any")
    assert len(info.value.errors) == 2 and info.value.errors[1]
    assert info.value.errors[0]["error_code"] == "INVALID_INPUT"
    assert info.value.errors[0]["status_code"] == HTTP_400


def test_quota_exceeded():
    headers = {"X-ELS-Status": QUOTA_ERROR_CODE}
    res = ResponseBundle(HTTP_429, headers, RAW_SERVICE_ERROR_QUOTA)
    with raises(ScopusAPIError) as info:
        ScopusResponse.validate_search(res)
    assert_http_error(info, HTTP_502, "any")
    assert len(info.value.errors) and info.value.errors[1]
    assert info.value.errors[0]["error_code"] == QUOTA_ERROR_CODE
    assert info.value.errors[0]["status_code"] == HTTP_429


def test_rate_limit_exceeded():
    headers = {"X-ELS-Status": RATE_LIMIT_ERROR_CODE}
    res = ResponseBundle(HTTP_429, headers, RAW_ERROR_RESPONSE_RATE_LIMIT)
    with raises(ScopusAPIError) as info:
        ScopusResponse.validate_search(res)
    assert_http_error(info, HTTP_502, "any")
    assert len(info.value.errors) and info.value.errors[1]
    assert info.value.errors[0]["error_code"] == RATE_LIMIT_ERROR_CODE
    assert info.value.errors[0]["status_code"] == HTTP_429


def test_json_validation_error():
    res = ResponseBundle(HTTP_200, RAW_HEADERS_OK, {"search-results": ""})
    with raises(InternalError) as info:
        ScopusResponse.validate_search(res)
    assert_http_error(info, HTTP_500, ExcMsg.VALIDATE_ERROR)
    assert info.value.errors[0]["type"] == fqn(ValidationError)
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]
    assert info.value.errors[0]["message"]
    assert info.value.errors[1]["type"] == "model_type"


def test_json_key_error():
    res = ResponseBundle(HTTP_200, RAW_HEADERS_OK, {"any": "any"})
    with raises(InternalError) as info:
        ScopusResponse.validate_search(res)
    assert_http_error(info, HTTP_500, ExcMsg.VALIDATE_ERROR)
    assert info.value.errors[0]["type"] == fqn(KeyError)
    assert info.value.errors[0]["file"] and info.value.errors[0]["line"]
    assert info.value.errors[0]["message"]
