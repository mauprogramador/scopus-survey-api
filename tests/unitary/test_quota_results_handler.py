from pytest import raises

from src.core.common.error_messages import (
    ARTICLES_NOT_FOUND,
    DATA_MISMATCH_ERROR,
)
from src.core.data.quota_results_handler import QuotaResultsHandler
from src.core.data.serializers import ScopusSearch
from src.core.domain.http_exceptions import (
    BadGateway,
    NotFound,
)
from tests.conftest import assert_http_error
from tests.mocks.helpers import search_raw
from tests.mocks.raw import (
    HTTP_404,
    HTTP_502,
    LOG_NO_QUOTA,
    LOG_ONE_QUOTA,
    LOG_QUOTA,
    RAW_SEARCH_NOT_FOUND,
)


STATE = QuotaResultsHandler()


def test_search_valid_data():
    first_search = ScopusSearch(**search_raw(7, 1))
    STATE.set_first_search(first_search)

    assert STATE.total_results == 7 and STATE.items_per_page == 7
    assert len(STATE.entry) == 1 and STATE.pages_count == 1
    assert not STATE.total_abstracts and not STATE.abstracts


def test_search_not_found():
    first_search = ScopusSearch(**RAW_SEARCH_NOT_FOUND)
    with raises(NotFound) as info:
        STATE.set_first_search(first_search)
    assert_http_error(info, HTTP_404, ARTICLES_NOT_FOUND)


def test_validate_integrity():
    first_search = ScopusSearch(**search_raw(1))
    STATE.set_first_search(first_search)
    STATE.validate_integrity()


def test_validate_integrity_error():
    first_search = ScopusSearch(**search_raw(156, 1))
    STATE.set_first_search(first_search)
    with raises(BadGateway) as info:
        STATE.validate_integrity()
    assert_http_error(info, HTTP_502, DATA_MISMATCH_ERROR)


def test_fix_total():
    first_search = ScopusSearch(**search_raw(156, 1))
    STATE.set_first_search(first_search)
    STATE.fix_total()

    assert STATE.total_abstracts == 1 and len(STATE.abstracts) == 0


def test_search_quota_greater():
    first_search = ScopusSearch(**search_raw(156, 1))
    STATE.set_first_search(first_search)

    assert STATE.total_results == 156 and STATE.items_per_page == 25
    assert len(STATE.entry) == 1 and STATE.pages_count == 7

    STATE.handle_search_quota(LOG_QUOTA)
    assert STATE.total_results == 156 and STATE.items_per_page == 25
    assert len(STATE.entry) == 1 and STATE.pages_count == 7

    assert STATE.pages_to_fetch == 6
    assert list(STATE.pages_to_fetch_range) == [1, 2, 3, 4, 5, 6]
    assert STATE.pages_to_fetch_progress == (156, 25, 1)


def test_search_quota_lesses():
    first_search = ScopusSearch(**search_raw(156, 1))
    STATE.set_first_search(first_search)

    assert STATE.total_results == 156 and STATE.items_per_page == 25
    assert len(STATE.entry) == 1 and STATE.pages_count == 7

    STATE.handle_search_quota(LOG_ONE_QUOTA)
    assert STATE.total_results == 26 and STATE.items_per_page == 25
    assert len(STATE.entry) == 1 and STATE.pages_count == 2
    assert STATE.pages_to_fetch == 1


def test_search_quota_exceeded():
    first_search = ScopusSearch(**search_raw(156, 1))
    STATE.set_first_search(first_search)

    assert STATE.total_results == 156 and STATE.items_per_page == 25
    assert len(STATE.entry) == 1 and STATE.pages_count == 7

    STATE.handle_search_quota(LOG_NO_QUOTA)
    assert STATE.total_results == 1 and STATE.items_per_page == 25
    assert len(STATE.entry) == 1 and STATE.pages_count == 1
    assert STATE.pages_to_fetch == 0


def test_abstract_quota_greater():
    first_search = ScopusSearch(**search_raw(156, 7))
    STATE.set_first_search(first_search)
    STATE.fix_total()

    assert STATE.total_abstracts == 7 and len(STATE.abstracts) == 0
    assert len(STATE.entry) == 7

    STATE.handle_abstract_quota(LOG_QUOTA)
    assert STATE.total_abstracts == 7 and len(STATE.abstracts) == 0
    assert len(STATE.entry) == 7

    assert STATE.abstracts_to_fetch == 6
    assert list(STATE.pages_to_fetch_range) == [1, 2, 3, 4, 5, 6]


def test_abstract_quota_lesser():
    first_search = ScopusSearch(**search_raw(156, 7))
    STATE.set_first_search(first_search)
    STATE.fix_total()

    assert STATE.total_abstracts == 7 and len(STATE.abstracts) == 0
    assert len(STATE.entry) == 7

    STATE.handle_abstract_quota(LOG_ONE_QUOTA)
    assert STATE.total_abstracts == 2 and len(STATE.abstracts) == 0
    assert len(STATE.entry) == 7 and STATE.abstracts_to_fetch == 1


def test_abstract_quota_exceeded():
    first_search = ScopusSearch(**search_raw(156, 7))
    STATE.set_first_search(first_search)
    STATE.fix_total()

    assert STATE.total_abstracts == 7 and len(STATE.abstracts) == 0
    assert len(STATE.entry) == 7

    STATE.handle_abstract_quota(LOG_NO_QUOTA)
    assert STATE.total_abstracts == 1 and len(STATE.abstracts) == 0
    assert len(STATE.entry) == 7 and STATE.abstracts_to_fetch == 0
