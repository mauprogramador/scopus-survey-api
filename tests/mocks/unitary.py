import itertools
import random
import string

from pandas import DataFrame

from src.core.common.types import CombinationBundle
from src.core.data.serializers import ScopusAbstract
from tests.mocks.errors import CONTENT_TYPE_ERROR, JSON_DECODE_ERROR
from tests.mocks.helpers import (
    abstract_raw,
    bundle_mock,
    headers_raw,
    response_mock,
    search_raw,
)
from tests.mocks.raw import (
    HTTP_429,
    HTTP_500,
    RAW_ABSTRACT_AUTHORS,
    RAW_ABSTRACT_FULL,
    RAW_ABSTRACT_OK,
    RAW_ERROR_RESPONSE_RATE_LIMIT,
    RAW_HEADERS_NO_QUOTA,
    RAW_HEADERS_ONE_QUOTA,
    RAW_SEARCH_NOT_FOUND,
    RAW_SEARCH_OK,
    RAW_SERVICE_ERROR_QUOTA,
)


# HTTPClient.request

GET_SUCCESS = response_mock(RAW_SEARCH_OK)
GET_CONTENT_TYPE_ERROR = response_mock(CONTENT_TYPE_ERROR)
GET_EMPTY_RESPONSE = response_mock(None)
GET_JSON_DECODE_ERROR = response_mock(JSON_DECODE_ERROR)
GET_RETRY = [
    response_mock(None, HTTP_500),
    response_mock(None, HTTP_500),
    response_mock(RAW_SEARCH_OK),
]
GET_RATE_LIMIT = [
    response_mock(
        RAW_ERROR_RESPONSE_RATE_LIMIT, HTTP_429, {"X-RateLimit-Remaining": "0"}
    ),
    GET_SUCCESS,
]

# ScopusSearchAPI.survey_totals_found

_COMBINATIONS = [
    (index, CombinationBundle(index=index, combination="any", url="any"))
    for index in range(1, 16)
]
TWO_KEYWORDS = dict(_COMBINATIONS[0:3])
FOUR_KEYWORDS = dict(_COMBINATIONS)

SURVEY_MAP = {
    index: bundle_mock(search_raw(random.randint(16, 256), 1))
    for index in range(1, 16)
}
SURVEY_RESULTS = list(SURVEY_MAP.values())
SURVEY_NOT_FOUND = [bundle_mock(RAW_SEARCH_NOT_FOUND)] * 3

# ScopusSearchAPI.search_articles

ONE_PAGE_ONE_RESULT = bundle_mock(RAW_SEARCH_OK)
ONE_PAGE_FULL_RESULTS = bundle_mock(search_raw(25, 1))
TWO_PAGES_PARTIAL_RESULTS = [bundle_mock(search_raw(30, 1))] * 2
TWO_PAGES_FULL_RESULTS = [bundle_mock(search_raw(50, 1))] * 2
MORE_PAGES_PARTIAL_RESULTS = [bundle_mock(search_raw(151, 1))] * 7
MORE_PAGES_FULL_RESULTS = [bundle_mock(search_raw(175, 1))] * 7
SEARCH_NOT_FOUND = bundle_mock(RAW_SEARCH_NOT_FOUND)
SEARCH_EXACT_QUOTA_ONE_RESULT = [
    bundle_mock(search_raw(1), headers=RAW_HEADERS_NO_QUOTA)
]
SEARCH_EXACT_QUOTA_TWO_RESULTS = [
    bundle_mock(search_raw(26, 1), headers=RAW_HEADERS_ONE_QUOTA),
    bundle_mock(search_raw(26, 1), headers=RAW_HEADERS_NO_QUOTA),
]
SEARCH_EXACT_QUOTA_MORE_RESULTS = [
    *[
        bundle_mock(search_raw(151, 1), headers=headers_raw(index))
        for index in range(6, 0, -1)
    ],
    bundle_mock(search_raw(151, 1), headers=RAW_HEADERS_NO_QUOTA),
]
SEARCH_NO_QUOTA_TWO_RESULTS = [
    bundle_mock(search_raw(26, 1), headers=RAW_HEADERS_NO_QUOTA)
]
SEARCH_NO_QUOTA_MORE_RESULTS = [
    *[
        bundle_mock(search_raw(151, 1), headers=headers_raw(index))
        for index in range(3, 0, -1)
    ],
    bundle_mock(search_raw(151, 1), headers=RAW_HEADERS_NO_QUOTA),
]
SEARCH_QUOTA_EXCEEDED = bundle_mock(
    RAW_SERVICE_ERROR_QUOTA, HTTP_429, RAW_HEADERS_NO_QUOTA
)

# ScopusabstractRetrievalAPI.retrieve_abstracts

ONE_ABSTRACT = bundle_mock(RAW_ABSTRACT_OK)
ONE_ABSTRACT_AUTHORS = bundle_mock(RAW_ABSTRACT_AUTHORS)
ONE_ABSTRACT_FULL = bundle_mock(RAW_ABSTRACT_FULL)
ABSTRACT_EXACT_QUOTA_ONE_RESULT = [
    bundle_mock(RAW_ABSTRACT_OK, headers=RAW_HEADERS_NO_QUOTA)
]
ABSTRACT_EXACT_QUOTA_TWO_RESULTS = [
    bundle_mock(RAW_ABSTRACT_OK, headers=RAW_HEADERS_ONE_QUOTA),
    bundle_mock(RAW_ABSTRACT_OK, headers=RAW_HEADERS_NO_QUOTA),
]
ABSTRACT_EXACT_QUOTA_MORE_RESULTS = [
    *[
        bundle_mock(RAW_ABSTRACT_OK, headers=headers_raw(index))
        for index in range(6, 0, -1)
    ],
    bundle_mock(RAW_ABSTRACT_OK, headers=RAW_HEADERS_NO_QUOTA),
]
ABSTRACT_NO_QUOTA_TWO_RESULTS = [
    bundle_mock(RAW_ABSTRACT_OK, headers=RAW_HEADERS_NO_QUOTA)
]
ABSTRACT_NO_QUOTA_MORE_RESULTS = [
    *[
        bundle_mock(RAW_ABSTRACT_OK, headers=headers_raw(index))
        for index in range(3, 0, -1)
    ],
    bundle_mock(RAW_ABSTRACT_OK, headers=RAW_HEADERS_NO_QUOTA),
]
ABSTRACT_QUOTA_EXCEEDED = bundle_mock(
    RAW_SERVICE_ERROR_QUOTA, HTTP_429, RAW_HEADERS_NO_QUOTA
)

# ArticlesSimilarityFilter.filter

ONE_GROUP_TWO_SIMILAR = DataFrame(
    {
        "authors": ["a", "a"],
        "title": ["any_a_1", "any_a_2"],
        "date": ["2025-05-01", "2025-06-01"],
    }
)
ONE_GROUP_MORE_SIMILAR = DataFrame(
    {
        "authors": ["a"] * 5,
        "title": [f"any_a_{index}" for index in range(1, 6)],
        "date": [f"2025-05-0{index}" for index in range(1, 6)],
    }
)
ONE_GROUP_NO_SIMILAR = DataFrame(
    {
        "authors": ["a", "a"],
        "title": ["abc", "def"],
        "date": ["2025-06-01", "2025-06-02"],
    }
)
MORE_GROUPS_TWO_SIMILAR = DataFrame(
    {
        "authors": ["a", "a", "b", "b", "c"],
        "title": ["any_a_1", "any_a_2", "any_b_1", "any_b_2", "any_c_1"],
        "date": [
            "2025-06-01",
            "2025-05-01",
            "2025-06-01",
            "2025-05-01",
            "2025-06-01",
        ],
    }
)
MORE_GROUPS_MORE_SIMILAR = DataFrame(
    {
        "authors": [*["a"] * 4, *["b"] * 3, "c", "c"],
        "title": [
            *[f"any_a_{index}" for index in range(1, 5)],
            *[f"any_b_{index}" for index in range(1, 4)],
            "any_c_1",
            "any_c_2",
        ],
        "date": [
            *[f"2025-06-0{index}" for index in range(1, 5)],
            *[f"2025-05-0{index}" for index in range(1, 4)],
            "2025-04-01",
            "2025-04-02",
        ],
    }
)
MORE_GROUPS_NO_SIMILAR = DataFrame(
    {
        "authors": [*["a"] * 4, *["b"] * 3, "c", "c"],
        "title": [
            *map("".join, itertools.batched(string.ascii_lowercase[:12], 3)),
            *map("".join, itertools.batched(string.ascii_lowercase[:9], 3)),
            "abc",
            "def",
        ],
        "date": [
            *[f"2025-06-0{index}" for index in range(1, 5)],
            *[f"2025-05-0{index}" for index in range(1, 4)],
            "2025-04-01",
            "2025-04-02",
        ],
    }
)
NO_DATETIME_LEFT = DataFrame(
    {
        "authors": ["a", "a"],
        "title": ["any_a_1", "any_a_2"],
        "date": ["NaN", "null"],
    }
)
ONE_DATETIME_LEFT = DataFrame(
    {
        "authors": ["a", "a"],
        "title": ["any_a_1", "any_a_2"],
        "date": ["2025-06-01", "null"],
    }
)
NO_REPEATED_AUTHORS = DataFrame(
    {
        "authors": ["a", "b"],
        "title": ["any", "any"],
        "date": ["2025-06-01", "2025-06-01"],
    }
)

# ScopusArticlesAggregator.retrieve_articles

DIFFERENT_ARTICLES = DataFrame(
    [
        ScopusAbstract(
            **abstract_raw(f"any_{letter}", letter, f"2025-06-0{index}")
        ).model_dump(by_alias=True)
        for index, letter in enumerate("abcdefg", 1)
    ]
)
EXACT_DUPLICATES = DataFrame(
    [ScopusAbstract(**RAW_ABSTRACT_OK).model_dump(by_alias=True)] * 2
)
SAME_TITLE_AND_AUTHORS = DataFrame(
    [
        ScopusAbstract(**abstract_raw()).model_dump(by_alias=True),
        ScopusAbstract(**abstract_raw()).model_dump(by_alias=True),
    ]
)
