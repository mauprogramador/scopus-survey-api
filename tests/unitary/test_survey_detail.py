from src.core.common.types import ResponseBundle
from src.core.data.serializers import ScopusSearch
from src.core.data.survey_details import SurveyDetails
from tests.mocks.raw import (
    HTTP_200,
    RAW_HEADERS_OK,
    RAW_SEARCH_OK,
    RESET_DATETIME,
)

SURVEY_DETAIL = SurveyDetails()


def test_search_data():
    model = ScopusSearch(**RAW_SEARCH_OK)
    SURVEY_DETAIL.set_search_data(model)
    assert SURVEY_DETAIL.headers["X-Total"] == "1"
    assert SURVEY_DETAIL.headers["X-Items-Per-Page"] == "1"
    assert SURVEY_DETAIL.headers["X-Pages-Count"] == "1"


def test_search_quota():
    res = ResponseBundle(HTTP_200, RAW_HEADERS_OK, {})
    SURVEY_DETAIL.set_search_quota(res)
    assert SURVEY_DETAIL.headers["X-Search-Limit"] == "20000"
    assert SURVEY_DETAIL.headers["X-Search-Remaining"] == "20000"
    assert SURVEY_DETAIL.headers["X-Search-Reset"] == RESET_DATETIME
    assert SURVEY_DETAIL.headers["X-Search-ELS-Status"] == "OK"


def test_abstract_quota():
    res = ResponseBundle(HTTP_200, RAW_HEADERS_OK, {})
    SURVEY_DETAIL.set_abstract_quota(res)
    assert SURVEY_DETAIL.headers["X-Abstract-Limit"] == "20000"
    assert SURVEY_DETAIL.headers["X-Abstract-Remaining"] == "20000"
    assert SURVEY_DETAIL.headers["X-Abstract-Reset"] == RESET_DATETIME
    assert SURVEY_DETAIL.headers["X-Abstract-ELS-Status"] == "OK"


def test_loss():
    SURVEY_DETAIL.set_loss(5, 13.5671)
    assert SURVEY_DETAIL.headers["X-Loss"] == "5doc / 13.57%"


def test_average_found():
    SURVEY_DETAIL.set_average_found(10000)
    assert SURVEY_DETAIL.headers["X-Average-Found"] == "~10,000"


def test_full_headers():
    assert len(SURVEY_DETAIL.log_data) == 2
    assert len(SURVEY_DETAIL.headers) == 13
