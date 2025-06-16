from pandas import DataFrame
from pydantic_core import PydanticUndefined

from src.core.data.serializers import ScopusAbstract, ScopusEntry
from tests.helpers.models import HeadersResponse, Request, Response
from tests.helpers.utils import abstract, entry_item, pagination

# adapters/gateway/scopus_search_api

ENTRIES = [entry_item(index) for index in range(7)]
ONE_PAGE = pagination(ENTRIES[:1])
TWO_PAGES = pagination(ENTRIES[:2])
MORE_PAGES = pagination(ENTRIES)
RESULTS = [ScopusEntry(**art) for art in ENTRIES]
EXCEEDED_RESPONSE = HeadersResponse()

# adapters/gateway/abstract_retrieval_api

ONE_ABSTRACT = Response(abstract())
ONE_ENTRY = [ScopusEntry(**ENTRIES[0])]
TWO_ENTRIES = [ScopusEntry(**art) for art in ENTRIES[:2]]
MORE_ENTRIES = [ScopusEntry(**art) for art in ENTRIES]
ARTICLES = DataFrame(
    [ScopusAbstract(**abstract()).model_dump(by_alias=True)] * 7
)


# core/usecases/articles_similarity_filter

TWO_SIMILAR_TITLES = DataFrame(
    {"Authors": ["a", "a"], "Title": ["any_a_1", "any_a_2"]}
)
__TITLES = ["any_a_1", "any_a_2", "any_b_1", "any_b_2", "any_c_1"]
MORE_SIMILAR_TITLES = DataFrame(
    {"Authors": ["a", "a", "b", "b", "c"], "Title": __TITLES}
)
NO_REPEATED_AUTHORS = DataFrame(
    {"Authors": ["a", "b"], "Title": ["any", "any"]}
)
NO_SIMILAR_TITLES = DataFrame({"Authors": ["a", "a"], "Title": ["abc", "def"]})

# core/usecases/scopus_articles_aggregator

EXACT_DUPLICATES = DataFrame(
    [ScopusAbstract(**abstract()).model_dump(by_alias=True)] * 2
)
SAME_TITLE_AND_AUTHORS = DataFrame(
    [
        ScopusAbstract(**abstract(doi="1")).model_dump(by_alias=True),
        ScopusAbstract(**abstract(doi="2")).model_dump(by_alias=True),
    ]
)

# adapters/presenters/exception_json

ERRORS = [{"type": "any", "loc": "any"}]
ERRORS_UNDEFINED = [{"input": PydanticUndefined}]
