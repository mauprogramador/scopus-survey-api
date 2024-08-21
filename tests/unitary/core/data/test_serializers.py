from math import ceil

from app.core.config.scopus import QUOTA_EXCEEDED
from app.core.data.serializers import Article, ScopusHeaders, ScopusJsonSchema
from tests.helpers.data import article
from tests.helpers.models import HeadersResponse
from tests.mocks.common import SCOPUS_API_JSON


def test_validate_scopus_json_schema():
    scopus_json = ScopusJsonSchema.model_validate(SCOPUS_API_JSON)

    assert scopus_json.total_results == 156
    assert scopus_json.items_per_page == 25
    assert scopus_json.pages_count == ceil(156 / 25)
    assert scopus_json.entry[0].title == "any"
    assert len(scopus_json.entry) == 1 and len(scopus_json.articles) == 1


def test_validate_article_model():
    article_model = Article.model_validate(article())
    article_data = article_model.model_dump(by_alias=True)

    assert len(article_data) == 8
    assert "@_fa" not in article_data
    assert article_model.link == "true"
    assert article_model.url == "any"
    assert article_model.volume == "any"
    assert article_model.date == "any"
    assert article_model.doi == "any"
    assert article_model.citations == "any"
    assert article_model.title == "any"
    assert article_model.scopus_id == "SCOPUS_ID:any"
    assert article_model.publication_name == "any"


def test_validate_scopus_headers():
    scopus_headers = ScopusHeaders.model_validate(HeadersResponse().headers)

    assert scopus_headers.reset == 1724320891
    assert QUOTA_EXCEEDED in scopus_headers.status
    assert scopus_headers.reset_datetime
    assert scopus_headers.quota_exceeded
