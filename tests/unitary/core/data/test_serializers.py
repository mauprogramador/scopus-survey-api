from math import ceil

from app.core.config.scopus import NULL, QUOTA_EXCEEDED
from app.core.data.serializers import (
    ScopusArticle,
    ScopusHeaders,
    ScopusResult,
    ScopusSearch,
)
from tests.helpers.models import HeadersResponse
from tests.helpers.utils import abstract
from tests.mocks.common import SCOPUS_API_JSON
from tests.mocks.unitary import SCOPUS_ARTICLE_JSON, SCOPUS_RESULT_JSON


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


def test_validate_scopus_headers():
    scopus_headers = ScopusHeaders.model_validate(HeadersResponse().headers)

    assert scopus_headers.reset == 1724320891
    assert QUOTA_EXCEEDED in scopus_headers.status
    assert scopus_headers.reset_datetime
    assert scopus_headers.quota_exceeded


def test_validate_scopus_article():
    model = ScopusArticle.model_validate(abstract())

    assert model.scopus_id == "SCOPUS_ID:any"
    assert model.url == NULL and model.abstract == NULL
    value = model.eid + model.title + model.publication_name + model.volume
    value = value + model.date + model.doi + model.citations + model.authors
    assert value.count("any") == 8


def test_validate_scopus_article_complete_response():
    model = ScopusArticle.model_validate(SCOPUS_ARTICLE_JSON)

    assert model.abstract == "any"
    assert model.authors == "any1, any2"
