import asyncio

from src.adapters.types import (
    Headers,
    HTTPClient,
    TotalBundle,
    URLBuilder,
)
from src.core.domain.types import CombinationParams, ScopusHeaders
from src.infra.http.fetch_multiple_concurrent import fetch_multiple
from src.infra.http.response_auditor import validate_search_response
from src.infra.http.url_builder import build_combination_urls
from src.infra.utils import logger


class ScopusVolumeScouter:
    """Search and retrieve articles via the Scopus Search API"""

    def __init__(self, http_client: HTTPClient) -> None:
        """Search and retrieve articles via the Scopus Search API"""
        self._http_client = http_client
        self._url_builder: URLBuilder = None

    async def _fetch_total(
        self, params: tuple[int, str]
    ) -> tuple[TotalBundle, Headers]:
        url = self._url_builder(params[1])
        res = await self._http_client.api_call(url)

        search = await asyncio.to_thread(validate_search_response, res)
        data: TotalBundle = {
            "index": params[0],
            "combination": params[1],
            "total": search.total_results,
        }

        return data, res.headers

    def _key(self, bundle: TotalBundle) -> int:
        return bundle["index"]

    async def _run(
        self, params: CombinationParams, combinations: list[str]
    ) -> tuple[list[TotalBundle], ScopusHeaders]:
        self._url_builder = build_combination_urls(params)

        results, quota_headers = await fetch_multiple(
            fetcher=self._fetch_total,
            params=enumerate(combinations, start=1),
            progress=range(len(combinations)),
        )
        results.sort(key=self._key)

        logger.quota(quota_headers, "search", allow_empty=True)

        return results, quota_headers

    async def fetch(
        self, params: CombinationParams, combinations: list[str]
    ) -> tuple[list[TotalBundle], ScopusHeaders]:
        try:
            return await self._run(params, combinations)
        finally:
            await self._http_client.close()
