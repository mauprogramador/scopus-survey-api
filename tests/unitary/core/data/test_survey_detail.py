from http import HTTPStatus

from src.core.data.serializers import ScopusQuotaRateLimit, ScopusSearch
from tests.helpers.models import ScopusResponse
from tests.mocks.fixtures import SURVEY_DETAIL


def test_set_scopus_search():
    model = ScopusSearch.model_validate(
        {
            "search-results": {
                "opensearch:totalResults": 156,
                "opensearch:itemsPerPage": 25,
                "entry": [],
            }
        }
    )
    SURVEY_DETAIL.set_scopus_search(model)


def test_set_response():
    headers = {
        "X-RateLimit-Limit": "20000",
        "X-RateLimit-Remaining": "20000",
        "X-RateLimit-Reset": "1746087344",
        "X-ELS-Status": "OK",
    }
    SURVEY_DETAIL.set_response(ScopusResponse(headers=headers))
    assert SURVEY_DETAIL.quota == ScopusQuotaRateLimit(**headers)
    assert SURVEY_DETAIL.code == HTTPStatus.OK
    assert SURVEY_DETAIL.quota.limit == 20000


def test_properties():
    SURVEY_DETAIL.max_count = 50
    assert len(SURVEY_DETAIL.log_data) == 2
    assert SURVEY_DETAIL.headers == {
        "X-Limit": "20000",
        "X-Remaining": "20000",
        "X-Reset": "1746087344",
        "X-ELS-Status": "OK",
        "X-Total": "156",
        "X-Items-Per-Page": "25",
        "X-Pages-Count": "7",
        "X-Max-Count": "50",
    }
