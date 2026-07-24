from pytest import mark

from src.adapters.gateway.scopus_dataset_gatherer import ScopusDatasetGatherer
from src.adapters.gateway.scopus_volume_scouter import ScopusVolumeScouter
from src.adapters.helpers.context import ScopusContext
from src.adapters.helpers.http_client import HTTPClient
from src.core.domain.factory import make_aggregator, make_combinator
from src.core.use_cases.similarity_filter import SimilarityFilter
from src.core.use_cases.survey_aggregator import SurveyAggregator
from src.core.use_cases.survey_combinations import SurveyCombinations


@mark.asyncio
async def test_make_combinator():
    use_case = make_combinator()
    api_gateway = getattr(use_case, "_api_gateway")
    http_client = getattr(api_gateway, "_http_client")

    assert use_case and isinstance(use_case, SurveyCombinations)
    assert api_gateway and isinstance(api_gateway, ScopusVolumeScouter)
    assert http_client and isinstance(http_client, HTTPClient)
    assert getattr(api_gateway, "_url_builder") is None

    await http_client.close()


# mypy: disable-error-code="annotation-unchecked"
@mark.asyncio
async def test_make_aggregator():
    use_case = make_aggregator()
    api_gateway = getattr(use_case, "_api_gateway")
    sim_filter = getattr(use_case, "_similarity_filter")
    http_client = getattr(api_gateway, "_http_client")
    context = getattr(api_gateway, "_ctx")

    assert use_case and isinstance(use_case, SurveyAggregator)
    assert api_gateway and isinstance(api_gateway, ScopusDatasetGatherer)
    assert sim_filter and isinstance(sim_filter, SimilarityFilter)
    assert http_client and isinstance(http_client, HTTPClient)
    assert context and isinstance(context, ScopusContext)

    assert getattr(api_gateway, "_search_url_builder") is None
    assert getattr(api_gateway, "_abstract_url_builder") is None

    await http_client.close()
