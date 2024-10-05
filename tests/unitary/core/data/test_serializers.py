from math import ceil

from app.core.config.scopus import NULL, QUOTA_EXCEEDED, RATE_LIMIT_EXCEEDED
from app.core.data.serializers import (
    ScopusAbstract,
    ScopusQuotaRateLimit,
    ScopusResult,
    ScopusSearch,
)
from tests.helpers.models import HeadersResponse
from tests.helpers.utils import abstract
from tests.mocks.common import SCOPUS_API_JSON
from tests.mocks.unitary import SCOPUS_ABSTRACT_JSON, SCOPUS_RESULT_JSON


def test_validate_scopus_result():
    model = ScopusResult.model_validate(SCOPUS_RESULT_JSON)

    assert model.link == "true"
    assert model.url == "any"
    assert model.scopus_id == "SCOPUS_ID:any"


def test_validate_scopus_search():
    scopus_json = ScopusSearch.model_validate(SCOPUS_API_JSON)

    assert scopus_json.total_results == 156
    assert scopus_json.items_per_page == 25
    assert scopus_json.pages_count == ceil(156 / 25)
    assert len(scopus_json.entry) == 0


def test_validate_scopus_quota_exceeded():
    status = ScopusQuotaRateLimit.model_validate(HeadersResponse())

    assert status.reset == 1724320891 and status.status == QUOTA_EXCEEDED
    assert status.reset_datetime and status.error_code == NULL
    assert status.quota_exceeded and not status.rate_limit_exceeded


def test_validate_scopus_rate_limit_exceeded():
    status = ScopusQuotaRateLimit.model_validate(HeadersResponse(True))

    assert status.reset == 1724320891 and status.status == NULL
    assert status.reset_datetime and status.error_code == RATE_LIMIT_EXCEEDED
    assert status.rate_limit_exceeded and not status.quota_exceeded


def test_validate_scopus_article():
    model = ScopusAbstract.model_validate(abstract())

    assert model.scopus_id == "SCOPUS_ID:any"
    assert model.abstract == NULL
    value = model.eid + model.title + model.publication_name + model.volume
    value = value + model.date + model.doi + model.citations + model.authors
    value = value + model.url
    assert value.count("any") == 9


def test_validate_scopus_article_complete_response():
    model = ScopusAbstract.model_validate(SCOPUS_ABSTRACT_JSON)

    assert model.abstract == "any"
    assert model.authors == "any1, any2"
