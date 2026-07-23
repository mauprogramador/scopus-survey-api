from src.core.common.types import (
    ResponseBundle,
    ScopusDetails,
    SurveyDetails,
    TotalBundle,
)
from src.core.data.serializers import ScopusHeaders, ScopusPage
from tests.mocks.raw import HTTP_200, RAW_HEADERS_OK, RAW_SEARCH_OK


_SEARCH_RESULT = ScopusPage(**RAW_SEARCH_OK)
_SEARCH_HEADERS = ScopusHeaders(**RAW_HEADERS_OK)
_ABSTRACT_HEADERS = ScopusHeaders(**RAW_HEADERS_OK)


def test_response_bundle():
    bundle = ResponseBundle(HTTP_200, {"any": "any"}, {"any": "any"})
    assert bundle.code == HTTP_200
    assert bundle.data == {"any": "any"}
    assert bundle.headers == {"any": "any"}


def test_total_bundle():
    bundle = TotalBundle({"index": 1, "combination": "any", "total": 7})
    assert bundle["index"] == 1
    assert bundle["combination"] == "any"
    assert bundle["total"] == 7


def test_scopus_details():
    bundle = ScopusDetails(
        _SEARCH_RESULT, 1, 7, _SEARCH_HEADERS, _ABSTRACT_HEADERS
    )
    assert id(bundle.search_result) == id(_SEARCH_RESULT)
    assert bundle.pages_count == 1 and bundle.total_retrieved == 7
    assert id(bundle.search_headers) == id(_SEARCH_HEADERS)
    assert id(bundle.abstract_headers) == id(_ABSTRACT_HEADERS)


def test_survey_details():
    bundle = SurveyDetails(
        _SEARCH_RESULT, 1, 7, _SEARCH_HEADERS, _ABSTRACT_HEADERS, 5
    )
    assert id(bundle.search_result) == id(_SEARCH_RESULT)
    assert bundle.pages_count == 1 and bundle.total_retrieved == 7
    assert id(bundle.search_headers) == id(_SEARCH_HEADERS)
    assert id(bundle.abstract_headers) == id(_ABSTRACT_HEADERS)
    assert bundle.total_final == 5
