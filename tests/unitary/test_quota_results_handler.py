from pytest import raises

from src.core.common.error_messages import QUOTA_EXCEEDED
from src.core.data.quota_results_handler import QuotaResultsHandler
from src.core.data.serializers import ScopusSearch
from src.core.domain.http_exceptions import TooManyRequests
from tests.conftest import assert_http_error
from tests.mocks.helpers import search_raw
from tests.mocks.raw import HTTP_429, LOG_NO_QUOTA, LOG_ONE_QUOTA, LOG_QUOTA


def test_search_valid_data():
    first_search = ScopusSearch(**search_raw(7))
    model = QuotaResultsHandler(first_search)

    assert model.total_results == 7 and model.items_per_page == 7
    assert len(model.entry) == 7 and model.pages_count == 1
    assert len(model.abstracts) == 0 and model.total_abstracts == 7


def test_search_quota_ok():
    first_search = ScopusSearch(**search_raw(156))
    model = QuotaResultsHandler(first_search)

    assert model.total_results == 156 and model.items_per_page == 25
    assert len(model.entry) == 25 and model.pages_count == 7
    assert len(model.abstracts) == 0 and model.total_abstracts == 156

    model.handle_search_quota(LOG_QUOTA)
    assert model.total_results == 156 and model.items_per_page == 25
    assert len(model.entry) == 25 and model.pages_count == 7
    assert len(model.abstracts) == 0 and model.total_abstracts == 156


def test_search_one_last_quota():
    first_search = ScopusSearch(**search_raw(156))
    model = QuotaResultsHandler(first_search)

    assert model.total_results == 156 and model.items_per_page == 25
    assert len(model.entry) == 25 and model.pages_count == 7
    assert len(model.abstracts) == 0 and model.total_abstracts == 156

    model.handle_search_quota(LOG_ONE_QUOTA)
    assert model.total_results == 50 and model.items_per_page == 25
    assert len(model.entry) == 25 and model.pages_count == 2
    assert len(model.abstracts) == 0 and model.total_abstracts == 50


def test_search_quota_exceeded():
    first_search = ScopusSearch(**search_raw(1))
    model = QuotaResultsHandler(first_search)

    assert model.total_results == 1 and model.items_per_page == 1
    assert len(model.entry) == 1 and model.pages_count == 1
    assert len(model.abstracts) == 0 and model.total_abstracts == 1

    with raises(TooManyRequests) as info:
        model.handle_search_quota(LOG_NO_QUOTA)
    assert_http_error(info, HTTP_429, QUOTA_EXCEEDED)


def test_abstract_quota_ok():
    first_search = ScopusSearch(**search_raw(156))
    model = QuotaResultsHandler(first_search)

    assert model.total_results == 156 and model.items_per_page == 25
    assert len(model.entry) == 25 and model.pages_count == 7
    assert len(model.abstracts) == 0 and model.total_abstracts == 156
    first_entry_item_id = id(model.entry[0])

    model.handle_abstract_quota(LOG_QUOTA)
    assert model.total_results == 156 and model.items_per_page == 25
    assert len(model.entry) == 24 and model.pages_count == 7
    assert len(model.abstracts) == 0 and model.total_abstracts == 156
    assert first_entry_item_id != id(model.entry[0])


def test_abstract_one_last_quota():
    first_search = ScopusSearch(**search_raw(156))
    model = QuotaResultsHandler(first_search)

    assert model.total_results == 156 and model.items_per_page == 25
    assert len(model.entry) == 25 and model.pages_count == 7
    assert len(model.abstracts) == 0 and model.total_abstracts == 156
    first_entry_item_id = id(model.entry[0])

    model.handle_abstract_quota(LOG_ONE_QUOTA)
    assert model.total_abstracts == 2 and len(model.entry) == 25
    assert first_entry_item_id == id(model.entry[0])


def test_abstract_quota_exceeded():
    first_search = ScopusSearch(**search_raw(1))
    model = QuotaResultsHandler(first_search)

    assert model.total_results == 1 and model.items_per_page == 1
    assert len(model.entry) == 1 and model.pages_count == 1
    assert len(model.abstracts) == 0 and model.total_abstracts == 1

    with raises(TooManyRequests) as info:
        model.handle_abstract_quota(LOG_NO_QUOTA)
    assert_http_error(info, HTTP_429, QUOTA_EXCEEDED)
