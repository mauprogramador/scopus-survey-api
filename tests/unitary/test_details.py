from src.core.common.types import SurveyDetails
from src.core.data.query_params import SurveyParams
from src.core.data.serializers import ScopusHeaders, ScopusPage
from src.framework.fastapi.details import extract_survey_details
from tests.mocks.raw import ALIAS_SEARCH_PARAMS, RAW_HEADERS_OK, RAW_SEARCH_OK


_SEARCH_RESULT = ScopusPage(**RAW_SEARCH_OK)
_SEARCH_HEADERS = ScopusHeaders(**RAW_HEADERS_OK)
_ABSTRACT_HEADERS = ScopusHeaders(**RAW_HEADERS_OK)


def test_details():
    params = SurveyParams(**ALIAS_SEARCH_PARAMS)
    details = SurveyDetails(
        _SEARCH_RESULT, 1, 7, _SEARCH_HEADERS, _ABSTRACT_HEADERS, 5
    )
    headers, metadata = extract_survey_details(params, details)

    assert len(headers) == 12
    assert headers["X-Combination"]
    assert headers["X-Scopus-Total"]
    assert headers["X-Total-Retrieved"]
    assert headers["X-Total-Final"]
    assert headers["X-Pages-Count"]
    assert headers["X-Items-Per-Page"]
    assert headers["X-Search-Limit"]
    assert headers["X-Search-Remaining"]
    assert headers["X-Search-Reset"]
    assert headers["X-Abstract-Limit"]
    assert headers["X-Abstract-Remaining"]
    assert headers["X-Abstract-Reset"]

    metadata_repr = ";".join(metadata)
    assert len(metadata) == 6
    assert "scopus_total=" in metadata_repr
    assert "items_per_page=" in metadata_repr
    assert "pages_count=" in metadata_repr
    assert "total_retrieved=" in metadata_repr
    assert "total_final=" in metadata_repr
    assert "loss=" in metadata_repr
