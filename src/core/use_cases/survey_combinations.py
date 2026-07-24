import itertools

from src.core.domain.types import (
    CombinationParams,
    Json,
    ScopusHeaders,
    VolumeScouter,
)
from src.infra.config.scopus import BOOLEAN_OPERATOR
from src.infra.utils import logger


class SurveyCombinations:
    """Map all keyword combination and survey their total in Scopus"""

    def __init__(self, api_gateway: VolumeScouter) -> None:
        """Map all keyword combination and survey their total in Scopus"""
        self._api_gateway = api_gateway

    async def process(
        self, params: CombinationParams
    ) -> tuple[list[Json], ScopusHeaders]:
        raw_combinations = (
            itertools.combinations(params.keywords, pairs_length)
            for pairs_length, _ in enumerate(params.keywords, start=1)
        )
        combinations = [
            BOOLEAN_OPERATOR.join(pairs)
            for pairs in itertools.chain.from_iterable(raw_combinations)
        ]

        results, quota_headers = await self._api_gateway.fetch(
            params, combinations
        )

        logger.combinations(len(params.keywords))

        return results, quota_headers
