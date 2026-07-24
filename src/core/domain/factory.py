from src.adapters.gateway.scopus_dataset_gatherer import ScopusDatasetGatherer
from src.adapters.gateway.scopus_volume_scouter import ScopusVolumeScouter
from src.core.use_cases import (
    SimilarityFilter,
    SurveyAggregator,
)
from src.core.use_cases.survey_combinations import SurveyCombinations
from src.infra.http.http_client import HTTPClient


def make_combinator() -> SurveyCombinations:
    http_client = HTTPClient()
    volume_scouter = ScopusVolumeScouter(http_client)

    return SurveyCombinations(volume_scouter)


def make_aggregator() -> SurveyAggregator:
    http_client = HTTPClient()
    dataset_gatherer = ScopusDatasetGatherer(http_client)
    similarity_filter = SimilarityFilter()

    return SurveyAggregator(dataset_gatherer, similarity_filter)
