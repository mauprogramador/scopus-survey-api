from src.core.common.types import ResponseBundle
from src.core.config.scopus import BOOLEAN_OPERATOR
from src.core.data.serializers import ScopusPage
from src.core.data.survey_details import SurveyDetails
from tests.mocks.raw import (
    HTTP_200,
    KEYWORDS,
    RAW_HEADERS_OK,
    RAW_SEARCH_OK,
    RESET_DATETIME,
)


SURVEY_DETAIL = SurveyDetails()


def test_keywords():
    SURVEY_DETAIL.set_keywords(KEYWORDS)
    assert SURVEY_DETAIL.headers["X-Keywords"] == BOOLEAN_OPERATOR.join(
        KEYWORDS
    )


def test_combination():
    SURVEY_DETAIL.set_combination("Python AND AI")
    assert SURVEY_DETAIL.headers["X-Combination"] == "Python AND AI"


def test_search_data():
    model = ScopusPage(**RAW_SEARCH_OK)
    SURVEY_DETAIL.set_search_data(model)
    assert SURVEY_DETAIL.headers["X-Total"] == "1"
    assert SURVEY_DETAIL.headers["X-Items-Per-Page"] == "1"
    assert SURVEY_DETAIL.headers["X-Pages-Count"] == "1"
    assert SURVEY_DETAIL.metadata[0] == "total=1"
    assert SURVEY_DETAIL.metadata[1] == "items_per_page=1"
    assert SURVEY_DETAIL.metadata[2] == "pages_count=1"


def test_search_quota():
    res = ResponseBundle(HTTP_200, RAW_HEADERS_OK, {})
    SURVEY_DETAIL.set_search_quota(res)
    assert SURVEY_DETAIL.headers["X-Search-Limit"] == "20000"
    assert SURVEY_DETAIL.headers["X-Search-Remaining"] == "20000"
    assert SURVEY_DETAIL.headers["X-Search-Reset"] == RESET_DATETIME


def test_abstract_quota():
    res = ResponseBundle(HTTP_200, RAW_HEADERS_OK, {})
    SURVEY_DETAIL.set_abstract_quota(res)
    assert SURVEY_DETAIL.headers["X-Abstract-Limit"] == "20000"
    assert SURVEY_DETAIL.headers["X-Abstract-Remaining"] == "20000"
    assert SURVEY_DETAIL.headers["X-Abstract-Reset"] == RESET_DATETIME


def test_results():
    SURVEY_DETAIL.set_results(1)
    assert SURVEY_DETAIL.headers["X-Results"] == "1doc / 1doc"
    assert SURVEY_DETAIL.metadata[3] == "results=1doc / 1doc"


def test_loss():
    SURVEY_DETAIL.set_loss(5, 13.5671)
    assert SURVEY_DETAIL.headers["X-Loss"] == "5doc / 13.57%"
    assert SURVEY_DETAIL.metadata[4] == "loss=5doc / 13.57%"


def test_full_headers():
    assert len(SURVEY_DETAIL.search_quota) == 2
    assert len(SURVEY_DETAIL.abstract_quota) == 2
    assert len(SURVEY_DETAIL.headers) == 13
    assert len(SURVEY_DETAIL.metadata) == 5
