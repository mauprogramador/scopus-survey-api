from src.core.common.types import ResponseBundle
from src.core.data.serializers import ScopusSearch
from src.core.data.survey_detail import SurveyDetail
from tests.mocks.raw import HTTP_200, RAW_HEADERS_OK, RAW_SEARCH_OK, RESET

SURVEY_DETAIL = SurveyDetail()


def test_search_data():
    model = ScopusSearch(**RAW_SEARCH_OK)
    SURVEY_DETAIL.set_search_data(model)
    assert SURVEY_DETAIL.headers["X-Total"] == "1"
    assert SURVEY_DETAIL.headers["X-Items-Per-Page"] == "1"
    assert SURVEY_DETAIL.headers["X-Pages-Count"] == "1"


def test_quota_data():
    res = ResponseBundle(HTTP_200, RAW_HEADERS_OK, {})
    SURVEY_DETAIL.set_quota_data(res)
    assert SURVEY_DETAIL.headers["X-Limit"] == "20000"
    assert SURVEY_DETAIL.headers["X-Remaining"] == "20000"
    assert SURVEY_DETAIL.headers["X-Reset"] == str(RESET)
    assert SURVEY_DETAIL.headers["X-ELS-Status"] == "OK"


def test_loss():
    SURVEY_DETAIL.set_loss(13.5671)
    assert SURVEY_DETAIL.headers["X-Loss"] == "13.57%"


def test_full_headers():
    assert len(SURVEY_DETAIL.log_data) == 2
    assert len(SURVEY_DETAIL.headers) == 9
