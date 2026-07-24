from unittest.mock import ANY

from src.adapters.gateway.context import ScopusContext
from src.adapters.serializers.scopus_data import ScopusPage
from tests.mocks.raw import RAW_SEARCH_OK


_SEARCH_RESULT = ScopusPage(**RAW_SEARCH_OK)


def test_survey_context():
    ctx = ScopusContext()
    assert not ctx.search_result
    assert not ctx.total_results
    assert not ctx.search_headers
    assert not ctx.abstract_headers
    assert not ctx.entry
    assert not ctx.abstracts
    assert ctx.items_per_page == 0
    assert ctx.pages_count == 0

    ctx.search_result = _SEARCH_RESULT
    ctx.total_results = _SEARCH_RESULT.total_results
    ctx.entry.append(ANY)
    ctx.abstracts.append(ANY)

    assert id(ctx.search_result) == id(_SEARCH_RESULT)
    assert ctx.items_per_page == _SEARCH_RESULT.items_per_page == 1
    assert ctx.pages_count == 1
    assert ctx.entry and ctx.abstracts
