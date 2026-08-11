import asyncio

from src.adapters.exceptions import DataSumMismatchError, ResourceNotFoundError
from src.adapters.gateway.context import ScopusContext
from src.adapters.serializers.scopus_data import ScopusHeaders
from src.adapters.types import Headers, HTTPClient, URLBuilder
from src.core.domain.types import (
    ExcMsg,
    Json,
    ScopusDetails,
    ScopusPage,
    SurveyParams,
)
from src.infra.http.fetch_multiple_concurrent import fetch_multiple
from src.infra.http.response_auditor import (
    validate_abstract_response,
    validate_search_response,
)
from src.infra.http.url_builder import (
    build_abstract_urls,
    build_search_urls,
)
from src.infra.utils import logger


class ScopusDatasetGatherer:
    """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""

    _INITIAL_PAGE = 0
    _FIRST_PAGE = 1
    _PAGE_TWO = 1

    def __init__(self, http_client: HTTPClient) -> None:
        """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""
        self._http_client = http_client
        self._search_url_builder: URLBuilder = None
        self._abstract_url_builder: URLBuilder = None
        self._ctx = ScopusContext()

    async def _fetch_page(self, index: int) -> tuple[ScopusPage, Headers]:
        start_page = index * self._ctx.items_per_page
        url = self._search_url_builder(start_page)

        res = await self._http_client.api_call(url)
        page = await asyncio.to_thread(validate_search_response, res)

        # Interface Segregation for ScopusPage
        return page, res.headers  # type: ignore[return-value]

    async def _fetch_abstract(self, index: int) -> tuple[Json, Headers]:
        url = self._abstract_url_builder(self._ctx.entry[index].url)

        res = await self._http_client.api_call(url)
        abstract = await asyncio.to_thread(validate_abstract_response, res)

        return abstract.model_dump(), res.headers

    def _validate_results(self) -> tuple[list[Json], ScopusDetails]:
        if self._ctx.total_results != len(self._ctx.abstracts):
            logger.debug(
                total_results=self._ctx.total_results,
                total_abstracts=len(self._ctx.abstracts),
            )
            raise DataSumMismatchError(ExcMsg.DATA_MISMATCH_ERROR)

        search_headers = ScopusHeaders.model_validate(self._ctx.search_headers)
        abstract_headers = ScopusHeaders.model_validate(
            self._ctx.abstract_headers
        )

        logger.quota(search_headers, "search")
        logger.quota(abstract_headers, "abstract")

        details = ScopusDetails(
            self._ctx.search_result,
            self._ctx.pages_count,
            len(self._ctx.abstracts),
            search_headers,
            abstract_headers,
        )

        return self._ctx.abstracts, details

    def _calculate_quota(self) -> None:
        remaining_abstract_quota = ScopusHeaders.model_validate(
            self._ctx.abstract_headers
        ).remaining

        assert remaining_abstract_quota is not None
        abstracts_to_fetch = self._ctx.total_results - self._FIRST_PAGE

        logger.debug(
            remaining_abstract_quota=remaining_abstract_quota,
            abstracts_to_fetch=abstracts_to_fetch,
            total_results=self._ctx.total_results,
        )

        if abstracts_to_fetch > remaining_abstract_quota:
            self._ctx.total_results = remaining_abstract_quota
            self._ctx.total_results += self._FIRST_PAGE

        remaining_search_quota = ScopusHeaders.model_validate(
            self._ctx.search_headers
        ).remaining

        assert remaining_search_quota is not None
        pages_to_fetch = self._ctx.pages_count - self._FIRST_PAGE

        logger.debug(
            remaining_search_quota=remaining_search_quota,
            pages_to_fetch=pages_to_fetch,
            total_results=self._ctx.total_results,
        )

        if pages_to_fetch > remaining_search_quota:
            pages_count = remaining_search_quota + self._FIRST_PAGE
            self._ctx.total_results = pages_count * self._ctx.items_per_page

        logger.debug(total_results=self._ctx.total_results)

    async def _run(
        self, params: SurveyParams
    ) -> tuple[list[Json], ScopusDetails]:
        self._search_url_builder = build_search_urls(params)

        search_result, self._ctx.search_headers = await self._fetch_page(
            index=self._INITIAL_PAGE
        )
        logger.total_found(search_result.total_results)

        if search_result.total_results == 0:
            raise ResourceNotFoundError(ExcMsg.ARTICLES_NOT_FOUND)

        self._ctx.entry.extend(search_result.entry)
        self._ctx.search_result = search_result
        self._ctx.total_results = search_result.total_results

        self._abstract_url_builder = build_abstract_urls(params.api_key)

        abstract_data, self._ctx.abstract_headers = await self._fetch_abstract(
            index=self._INITIAL_PAGE
        )
        self._ctx.abstracts.append(abstract_data)

        self._calculate_quota()

        if self._ctx.total_results == 1:
            return self._validate_results()

        if self._ctx.total_results == 2:
            abstract_data, self._ctx.abstract_headers = (
                await self._fetch_abstract(index=self._PAGE_TWO)
            )
            self._ctx.abstracts.append(abstract_data)

            return self._validate_results()

        if self._ctx.pages_count == 2:
            page, self._ctx.search_headers = await self._fetch_page(
                index=self._PAGE_TWO
            )
            self._ctx.entry.extend(page.entry)

        elif self._ctx.pages_count > 2:
            pages_to_fetch = range(self._FIRST_PAGE, self._ctx.pages_count)

            results, self._ctx.search_headers = await fetch_multiple(
                self._fetch_page, pages_to_fetch, pages_to_fetch
            )

            for page in results:
                self._ctx.entry.extend(page.entry)

        abstracts_to_fetch = range(self._FIRST_PAGE, self._ctx.total_results)

        results, self._ctx.abstract_headers = await fetch_multiple(
            self._fetch_abstract, abstracts_to_fetch, abstracts_to_fetch
        )
        self._ctx.abstracts.extend(results)

        return self._validate_results()

    async def fetch(
        self, params: SurveyParams
    ) -> tuple[list[Json], ScopusDetails]:
        try:
            return await self._run(params)
        finally:
            await self._http_client.close()
