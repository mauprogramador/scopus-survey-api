from random import randint

from pandas import DataFrame

from src.core.common.types import CombinationBundle
from src.core.data.enums import Column
from src.core.data.serializers import ScopusAbstract, ScopusEntry, ScopusSearch
from tests.mocks.errors import CONTENT_TYPE_ERROR, JSON_DECODE_ERROR
from tests.mocks.helpers import abstract_raw, response_mock, search_raw
from tests.mocks.raw import (
    HTTP_500,
    RAW_ABSTRACT_AUTHORS,
    RAW_ABSTRACT_FULL,
    RAW_ABSTRACT_OK,
    RAW_ENTRY,
    RAW_SEARCH_OK,
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

# ScopusSearchAPI.survey_totals_found

_COMBINATIONS = [
    (index, CombinationBundle(index=index, combination="any", url="any"))
    for index in range(1, 16)
]
TWO_KEYWORDS = dict(_COMBINATIONS[0:3])
FOUR_KEYWORDS = dict(_COMBINATIONS)

SURVEY_MAP = {
    index: ScopusSearch(**search_raw(randint(16, 256), 1))
    for index in range(1, 16)
}
SURVEY_RESULTS = list(SURVEY_MAP.values())

# ScopusSearchAPI.search_articles

ONE_PAGE_ONE_RESULT = ScopusSearch(**RAW_SEARCH_OK)
ONE_PAGE_FULL_RESULTS = ScopusSearch(**search_raw(25))
TWO_PAGES_PARTIAL_RESULTS = [
    ScopusSearch(**search_raw(30)),  # 1st instance independent
    ScopusSearch(**search_raw(30, 5)),
]
TWO_PAGES_FULL_RESULTS = [
    ScopusSearch(**search_raw(50)),  # 1st instance independent
    ScopusSearch(**search_raw(50)),
]
MORE_PAGES_PARTIAL_RESULTS = [
    ScopusSearch(**search_raw(151)),  # 1st instance independent
    *[ScopusSearch(**search_raw(151))] * 5,
    ScopusSearch(**search_raw(151, 1)),
]
MORE_PAGES_FULL_RESULTS = [
    ScopusSearch(**search_raw(175)),  # 1st instance independent
    *[ScopusSearch(**search_raw(175))] * 6,
]

# ScopusabstractRetrievalAPI.retrieve_abstracts

ENTRIES = [ScopusEntry(**RAW_ENTRY)] * 7
ONE_ABSTRACT = ScopusAbstract(**RAW_ABSTRACT_OK)
ONE_ABSTRACT_AUTHORS = ScopusAbstract(**RAW_ABSTRACT_AUTHORS)
ONE_ABSTRACT_FULL = ScopusAbstract(**RAW_ABSTRACT_FULL)

# ArticlesSimilarityFilter.filter

ONE_GROUP_TWO_SIMILAR = DataFrame(
    {
        Column.AUTHORS: ["a", "a"],
        Column.TITLE: ["any_a_1", "any_a_2"],
        Column.DATE: ["2025-05-01", "2025-06-01"],
    }
)
ONE_GROUP_MORE_SIMILAR = DataFrame(
    {
        Column.AUTHORS: ["a"] * 5,
        Column.TITLE: [f"any_a_{index}" for index in range(1, 6)],
        Column.DATE: [f"2025-05-0{index}" for index in range(1, 6)],
    }
)
MORE_GROUPS_TWO_SIMILAR = DataFrame(
    {
        Column.AUTHORS: ["a", "a", "b", "b", "c"],
        Column.TITLE: ["any_a_1", "any_a_2", "any_b_1", "any_b_2", "any_c_1"],
        Column.DATE: [
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
        Column.AUTHORS: [*["a"] * 4, *["b"] * 3, "c", "c"],
        Column.TITLE: [
            *[f"any_a_{index}" for index in range(1, 5)],
            *[f"any_b_{index}" for index in range(1, 4)],
            "any_c_1",
            "any_c_2",
        ],
        Column.DATE: [
            *[f"2025-06-0{index}" for index in range(1, 5)],
            *[f"2025-05-0{index}" for index in range(1, 4)],
            "2025-04-01",
            "2025-04-02",
        ],
    }
)
NO_DATETIME_LEFT = DataFrame(
    {
        Column.AUTHORS: ["a", "a"],
        Column.TITLE: ["any_a_1", "any_a_2"],
        Column.DATE: ["NaN", "null"],
    }
)
ONE_DATETIME_LEFT = DataFrame(
    {
        Column.AUTHORS: ["a", "a"],
        Column.TITLE: ["any_a_1", "any_a_2"],
        Column.DATE: ["2025-06-01", "null"],
    }
)
NO_REPEATED_AUTHORS = DataFrame(
    {
        Column.AUTHORS: ["a", "b"],
        Column.TITLE: ["any", "any"],
        Column.DATE: ["2025-06-01", "2025-06-01"],
    }
)
NO_SIMILAR_TITLES = DataFrame(
    {
        Column.AUTHORS: ["a", "a"],
        Column.TITLE: ["abc", "def"],
        Column.DATE: ["2025-06-01", "2025-06-02"],
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
