from datetime import datetime
from itertools import batched  # type: ignore
from string import ascii_lowercase
from time import time

from src.core.data.enums import ScopusCode
from tests.mocks.errors import CONTENT_TYPE_ERROR, JSON_DECODE_ERROR
from tests.mocks.helpers import abstract_raw, response_mock, search_raw
from tests.mocks.raw import (
    HTTP_429,
    HTTP_500,
    RAW_ABSTRACT_AUTHORS,
    RAW_ABSTRACT_FULL,
    RAW_ABSTRACT_OK,
    RAW_ERROR_RESPONSE_RATE_LIMIT,
    RAW_SEARCH_NOT_FOUND,
    RAW_SEARCH_OK,
    RAW_SERVICE_ERROR_QUOTA,
)

# Routes

COMBINATION_RESPONSES = [response_mock(RAW_SEARCH_OK)] * 3
SURVEY_RESPONSES = [
    response_mock(RAW_SEARCH_OK),
    response_mock(RAW_ABSTRACT_OK),
]

# HTTPClient.request

GET_SUCCESS = [response_mock(RAW_SEARCH_OK)] * 3
GET_CONTENT_TYPE_ERROR = response_mock(CONTENT_TYPE_ERROR)
GET_EMPTY_RESPONSE = response_mock(None)
GET_JSON_DECODE_ERROR = response_mock(JSON_DECODE_ERROR)
GET_RETRY = [
    response_mock(None, HTTP_500),
    response_mock(None, HTTP_500),
    response_mock(RAW_SEARCH_OK),
]

# ScopusSearchAPI.survey_totals_found

SURVEY_TWO_KEYWORDS = [response_mock(RAW_SEARCH_OK)] * 3
SURVEY_THREE_KEYWORDS = [response_mock(RAW_SEARCH_OK)] * 7
SURVEY_FOUR_KEYWORDS = [response_mock(RAW_SEARCH_OK)] * 15
SURVEY_NOT_FOUND = [response_mock(RAW_SEARCH_NOT_FOUND)] * 3
SURVEY_CANCELLED_ERROR = [response_mock(RAW_SEARCH_NOT_FOUND)] * 15

# ScopusSearchAPI.search_articles

SEARCH_ONE_PAGE_ONE_RESULT = [
    response_mock(RAW_SEARCH_OK),
    response_mock(RAW_ABSTRACT_OK),
]
SEARCH_ONE_PAGE_FULL_RESULTS = [
    response_mock(search_raw(25)),
    *[response_mock(RAW_ABSTRACT_OK)] * 25,
]
SEARCH_TWO_PAGES_PARTIAL_RESULTS = [
    response_mock(search_raw(30)),
    response_mock(search_raw(30, 5)),
    *[response_mock(RAW_ABSTRACT_OK)] * 30,
]
SEARCH_TWO_PAGES_FULL_RESULTS = [
    response_mock(search_raw(50)),
    response_mock(search_raw(50)),
    *[response_mock(RAW_ABSTRACT_OK)] * 50,
]
SEARCH_MORE_PAGES_PARTIAL_RESULTS = [
    *[response_mock(search_raw(151))] * 6,
    response_mock(search_raw(151, 1)),
    *[response_mock(RAW_ABSTRACT_OK)] * 151,
]
SEARCH_MORE_PAGES_FULL_RESULTS = [
    *[response_mock(search_raw(175))] * 7,
    *[response_mock(RAW_ABSTRACT_OK)] * 175,
]
SEARCH_NOT_FOUND = response_mock(RAW_SEARCH_NOT_FOUND)
SEARCH_CANCELLED_ERROR = [response_mock(search_raw(125))] * 5

# ScopusabstractRetrievalAPI.retrieve_abstracts

RETRIEVE_ONE_PARTIAL_ABSTRACT = [
    response_mock(RAW_SEARCH_OK),
    response_mock(RAW_ABSTRACT_OK),
]
RETRIEVE_ONE_ABSTRACT_AUTHORS = [
    response_mock(RAW_SEARCH_OK),
    response_mock(RAW_ABSTRACT_AUTHORS),
]
RETRIEVE_ONE_ABSTRACT_FULL = [
    response_mock(RAW_SEARCH_OK),
    response_mock(RAW_ABSTRACT_FULL),
]
RETRIEVE_TWO_ABSTRACTS = [
    response_mock(search_raw(2)),
    *[response_mock(RAW_ABSTRACT_OK)] * 2,
]
RETRIEVE_MORE_ABSTRACTS = [
    response_mock(search_raw(25)),
    *[response_mock(RAW_ABSTRACT_OK)] * 25,
]
RETRIEVE_CANCELLED_ERROR = [
    response_mock(search_raw(7)),
    *[response_mock(RAW_ABSTRACT_OK)] * 7,
]

# ScopusResponse.validate_

RESPONSE_STATUS_ERROR = response_mock(
    {"error": "any"}, headers={"X-ELS-Status": "ERROR"}
)
RESPONSE_QUOTA_EXCEEDED = response_mock(
    RAW_SERVICE_ERROR_QUOTA, HTTP_429, {"X-ELS-Status": ScopusCode.QUOTA}
)
RESPONSE_RATE_LIMIT_EXCEEDED = response_mock(
    RAW_ERROR_RESPONSE_RATE_LIMIT,
    HTTP_429,
    {"X-ELS-Status": ScopusCode.RATE_LIMIT},
)
RESPONSE_JSON_ERROR = response_mock({"search-results": ""})
RESPONSE_KEY_ERROR = response_mock({"any": "any"})

# SurveyDetail.set_

RESET = int(time() + 60)
RESET_DATETIME = datetime.fromtimestamp(RESET).strftime("%Y-%m-%d %H:%M:%S")
HEADERS = {
    "X-RateLimit-Limit": "20000",
    "X-RateLimit-Remaining": "12345",
    "X-RateLimit-Reset": str(RESET),
    "X-ELS-Status": "OK",
}
COMBINATION_DETAILS = [
    response_mock(RAW_SEARCH_OK),
    response_mock(RAW_SEARCH_OK),
    response_mock(RAW_SEARCH_OK, headers=HEADERS),
]
SEARCH_DETAILS_ONE_RESULT = [
    response_mock(RAW_SEARCH_OK, headers=HEADERS),
    response_mock(RAW_ABSTRACT_OK, headers=HEADERS),
]
SEARCH_DETAILS_MORE_RESULTS = [
    response_mock(search_raw(3), headers=HEADERS),
    response_mock(RAW_ABSTRACT_OK, headers=HEADERS),
    response_mock(RAW_ABSTRACT_OK, headers=HEADERS),
    response_mock(RAW_ABSTRACT_OK, headers=HEADERS),
]

# ArticlesSimilarityFilter.filter

ONE_GROUP_TWO_SIMILAR = [
    response_mock(search_raw(2)),
    response_mock(abstract_raw("any_a_1", "a", "2025-06-01")),
    response_mock(abstract_raw("any_a_2", "a", "2025-06-02")),
]
ONE_GROUP_MORE_SIMILAR = [
    response_mock(search_raw(5)),
    *[
        response_mock(abstract_raw(f"any_a_{index}", "a", f"2025-06-0{index}"))
        for index in range(1, 6)
    ],
]
ONE_GROUP_NO_SIMILAR = [
    response_mock(search_raw(2)),
    response_mock(abstract_raw("abc", "a", "2025-06-01")),
    response_mock(abstract_raw("def", "a", "2025-06-02")),
]
MORE_GROUPS_TWO_SIMILAR = [
    response_mock(search_raw(5)),
    response_mock(abstract_raw("any_a_1", "a", "2025-06-01")),
    response_mock(abstract_raw("any_a_2", "a", "2025-06-05")),
    response_mock(abstract_raw("any_b_1", "b", "2025-06-01")),
    response_mock(abstract_raw("any_b_2", "b", "2025-06-05")),
    response_mock(abstract_raw("any_c_1", "c", "2025-06-01")),
]
MORE_GROUPS_MORE_SIMILAR = [
    response_mock(search_raw(9)),
    *[
        response_mock(abstract_raw(f"any_a_{index}", "a", f"2025-06-0{index}"))
        for index in range(1, 5)
    ],
    *[
        response_mock(abstract_raw(f"any_b_{index}", "b", f"2025-06-0{index}"))
        for index in range(1, 4)
    ],
    response_mock(abstract_raw("any_c_1", "c", "2025-06-01")),
    response_mock(abstract_raw("any_c_2", "c", "2025-06-02")),
]
MORE_GROUPS_NO_SIMILAR = [
    response_mock(search_raw(9)),
    *[
        response_mock(abstract_raw("".join(item), "a", "2025-06-01"))
        for item in batched(ascii_lowercase[:12], 3)
    ],
    *[
        response_mock(abstract_raw("".join(item), "b", "2025-06-01"))
        for item in batched(ascii_lowercase[:9], 3)
    ],
    response_mock(abstract_raw("abc", "c", "2025-06-01")),
    response_mock(abstract_raw("def", "c", "2025-06-02")),
]
NO_DATETIME_LEFT = [
    response_mock(search_raw(2)),
    response_mock(abstract_raw("any_a_1", "a", "NaN")),
    response_mock(abstract_raw("any_a_2", "a", "null")),
]
ONE_DATETIME_LEFT = [
    response_mock(search_raw(2)),
    response_mock(abstract_raw("any_a_1", "a", "2025-06-01")),
    response_mock(abstract_raw("any_a_2", "a", "null")),
]
NO_REPEATED_AUTHORS = [
    response_mock(search_raw(2)),
    response_mock(abstract_raw("any", "a", "2025-06-01")),
    response_mock(abstract_raw("any", "b", "2025-06-01")),
]

# ScopusArticlesAggregator.retrieve_articles

ONE_DIFFERENT_ARTICLE = [
    response_mock(RAW_SEARCH_OK),
    response_mock(RAW_ABSTRACT_OK),
]
MORE_DIFFERENT_ARTICLES = [
    response_mock(search_raw(7)),
    *[
        response_mock(
            abstract_raw(f"any_{letter}", letter, f"2025-06-0{index}")
        )
        for index, letter in enumerate("abcdefg", 1)
    ],
]
EXACT_DUPLICATES = [
    response_mock(search_raw(2)),
    response_mock(RAW_ABSTRACT_OK),
    response_mock(RAW_ABSTRACT_OK),
]
SAME_TITLE_AND_AUTHORS = [
    response_mock(search_raw(2)),
    response_mock(abstract_raw()),
    response_mock(abstract_raw()),
]
