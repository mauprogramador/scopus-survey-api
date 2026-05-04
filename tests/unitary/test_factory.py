from pytest import mark

from src.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from src.adapters.gateway.scopus_search_api import ScopusSearchAPI
from src.adapters.helpers.http_client import HTTPClient
from src.adapters.helpers.url_builder import URLBuilder
from src.core.data.quota_results_handler import QuotaResultsHandler
from src.core.data.survey_details import SurveyDetails
from src.core.domain.factory import make_aggregator, make_combinator
from src.core.use_cases.articles_similarity_filter import (
    ArticlesSimilarityFilter,
)
from src.core.use_cases.keyword_combination_finder import (
    KeywordCombinationFinder,
)
from src.core.use_cases.scopus_articles_aggregator import (
    ScopusArticlesAggregator,
)


@mark.asyncio
async def test_make_combinator():
    use_case = make_combinator()

    use_case_builder = getattr(use_case, "_url_builder")
    search_api = getattr(use_case, "_search_api")
    use_case_details = getattr(use_case, "_details")

    client: HTTPClient = getattr(search_api, "_http_client")  # type: ignore
    await client.close()
    search_api_builder = getattr(search_api, "_url_builder")
    search_api_details = getattr(search_api, "_details")
    state = getattr(search_api, "_state")

    assert use_case and isinstance(use_case, KeywordCombinationFinder)
    assert search_api and isinstance(search_api, ScopusSearchAPI)
    assert client and isinstance(client, HTTPClient)
    assert search_api_builder and search_api_details
    assert use_case_builder and isinstance(use_case_builder, URLBuilder)
    assert id(use_case_builder) == id(search_api_builder)
    assert use_case_details and isinstance(use_case_details, SurveyDetails)
    assert id(use_case_details) == id(search_api_details)
    assert state is None


# mypy: disable-error-code="annotation-unchecked"
@mark.asyncio
async def test_make_aggregator():
    use_case = make_aggregator()

    search_api = getattr(use_case, "_search_api")
    abstract_api = getattr(use_case, "_abstract_api")
    similarity_filter = getattr(use_case, "_similarity_filter")
    use_case_details = getattr(use_case, "_details")

    search_client: HTTPClient = getattr(search_api, "_http_client")
    await search_client.close()
    search_builder = getattr(search_api, "_url_builder")
    search_details = getattr(search_api, "_details")
    search_state = getattr(search_api, "_state")

    abstract_client: HTTPClient = getattr(abstract_api, "_http_client")
    await abstract_client.close()
    abstract_builder = getattr(abstract_api, "_url_builder")
    abstract_details = getattr(abstract_api, "_details")
    abstract_state = getattr(abstract_api, "_state")

    assert use_case and isinstance(use_case, ScopusArticlesAggregator)
    assert similarity_filter and isinstance(
        similarity_filter, ArticlesSimilarityFilter
    )
    assert search_api and isinstance(search_api, ScopusSearchAPI)
    assert abstract_api and isinstance(
        abstract_api, ScopusAbstractRetrievalAPI
    )
    assert abstract_builder and abstract_details and use_case_details

    assert search_client and isinstance(search_client, HTTPClient)
    assert abstract_client and isinstance(abstract_client, HTTPClient)
    assert id(search_client) == id(abstract_client)

    assert search_builder and isinstance(search_builder, URLBuilder)
    assert id(search_builder) == id(abstract_builder)

    assert search_details and isinstance(search_details, SurveyDetails)
    assert id(search_details) == id(abstract_details) == id(use_case_details)

    assert search_state and isinstance(search_state, QuotaResultsHandler)
    assert id(search_state) == id(abstract_state)
