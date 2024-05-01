from app.core.model import ScopusResponse
from tests.data import mocks


def test_validate_model():
    json = mocks.SCOPUS_RESPONSE_JSON
    scopus_response = ScopusResponse.model_validate(json)
    assert scopus_response.total_results == 156
    assert scopus_response.items_per_page == 25
    assert scopus_response.count == int(156 / 25) + 1
    assert len(scopus_response.entry) == 0
