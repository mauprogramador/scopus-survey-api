from pydantic import ValidationError
from pytest import raises

from src.adapters.helpers.url_builder import build_article_page_url
from src.core.config.scopus import (
    QUOTA_ERROR_CODE,
    RATE_LIMIT_ERROR_CODE,
)
from src.core.data.serializers import (
    ScopusAbstract,
    ScopusEntry,
    ScopusError,
    ScopusHeaders,
    ScopusPage,
)
from tests.mocks.helpers import search_raw
from tests.mocks.raw import (
    ABSTRACT_URL,
    RAW_ABSTRACT_AUTHORS,
    RAW_ABSTRACT_FULL,
    RAW_ABSTRACT_OK,
    RAW_ENTRY,
    RAW_ERROR_RESPONSE_RATE_LIMIT,
    RAW_HEADERS_OK,
    RAW_SEARCH_NOT_FOUND,
    RAW_SERVICE_ERROR_QUOTA,
    RESET,
    SCOPUS_ID,
)


def test_scopus_entry_valid_data():
    model = ScopusEntry(**RAW_ENTRY)
    assert model.force_array == "true"
    assert model.url == ABSTRACT_URL and model.scopus_id == SCOPUS_ID


def test_scopus_entry_raise_errors():
    with raises(ValidationError) as info:
        ScopusEntry(**{})
    assert info.value.error_count() == 3


def test_scopus_search_valid_data():
    model = ScopusPage(**search_raw(156, 1))
    assert model.total_results == 156 and model.items_per_page == 25
    assert len(model.entry) == 1


def test_scopus_search_raise_errors():
    with raises(ValidationError) as info:
        ScopusPage(**{"search-results": {}})
    assert info.value.error_count() == 3


def test_scopus_search_key_error():
    with raises(ValidationError) as info:
        ScopusPage(**{})
    assert info.value.error_count() == 3


def test_scopus_search_empty_result():
    model = ScopusPage(**RAW_SEARCH_NOT_FOUND)
    assert model.total_results == 0 and model.items_per_page == 0
    assert len(model.entry) == 0


def test_scopus_abstract_valid_data():
    model = ScopusAbstract(**RAW_ABSTRACT_OK)
    assert model.url == build_article_page_url("0123456789")
    assert model.scopus_id == SCOPUS_ID
    assert model.authors == "any_author" and model.title == "any_title"
    assert model.publication_name is None and model.abstract is None
    assert model.date is None and model.eid is None and model.doi is None
    assert model.volume is None and model.citations is None


def test_scopus_abstract_overridden_default():
    model = ScopusAbstract(**RAW_ABSTRACT_FULL)
    assert model.url == build_article_page_url("0123456789")
    assert model.scopus_id == SCOPUS_ID
    assert model.authors == "any_author" and model.title == "any_title"
    assert model.publication_name == "any_publication_name"
    assert model.abstract == "any_abstract" and model.date == "any_date"
    assert model.eid == "any_eid" and model.doi == "any_doi"
    assert model.volume == "any_volume"
    assert model.citations == "any_citations"


def test_scopus_abstract_raise_errors():
    raw = {"abstracts-retrieval-response": {"coredata": {}}}
    with raises(ValidationError) as info:
        ScopusAbstract(**raw)
    assert info.value.error_count() == 2


def test_scopus_abstract_key_error():
    with raises(ValidationError) as info:
        ScopusAbstract(**{})
    assert info.value.error_count() == 2

    with raises(ValidationError) as info:
        ScopusAbstract(**{"abstracts-retrieval-response": {}})
    assert info.value.error_count() == 2


def test_scopus_abstract_no_author():
    raw = {
        "abstracts-retrieval-response": {
            "coredata": {
                "dc:identifier": SCOPUS_ID,
                "dc:title": "any_title",
            }
        }
    }
    model = ScopusAbstract(**raw)
    assert model.url == build_article_page_url("0123456789")
    assert model.scopus_id == SCOPUS_ID
    assert model.title == "any_title" and model.authors is None


def test_scopus_abstract_authors():
    model = ScopusAbstract(**RAW_ABSTRACT_AUTHORS)
    assert model.url == build_article_page_url("0123456789")
    assert model.scopus_id == SCOPUS_ID
    assert model.authors == "any_author_1, any_author_2"


def test_scopus_headers_valid_data():
    model = ScopusHeaders(**{})
    assert model.limit is None and model.remaining is None
    assert model.reset is None and model.status is None
    assert model.reset_datetime is None


def test_scopus_headers_overridden_default():
    model = ScopusHeaders(**RAW_HEADERS_OK)
    assert model.limit == 20000 and model.remaining == 20000
    assert model.reset == RESET and model.status == "OK"
    assert model.reset_datetime


def test_scopus_error_valid_data():
    with raises(ValidationError) as info:
        ScopusError(**{})
    assert info.value.error_count() == 2


def test_scopus_error_overridden_default():
    model = ScopusError(**RAW_SERVICE_ERROR_QUOTA)
    assert model.code == QUOTA_ERROR_CODE and model.text

    model = ScopusError(**RAW_ERROR_RESPONSE_RATE_LIMIT)
    assert model.code == RATE_LIMIT_ERROR_CODE and model.text


def test_scopus_error_key_error():
    with raises(ValidationError) as info:
        ScopusError(**{"service-error": {}})
    assert info.value.error_count() == 2
