import asyncio

from src.adapters.helpers.response_auditor import validate_search_response
from src.core.common.types import (
    CombinationBundle,
    HTTPClient,
    Json,
    ResponseBundle,
    SurveyDetails,
    SurveyParams,
    SurveyState,
    URLBuilder,
)
from src.core.data.enums import ExcMsg
from src.core.data.serializers import ScopusPage
from src.core.domain.http_exceptions import HTTPError, InternalError
from src.utils import logger
from src.utils.progress_bar import progress_bar


class ScopusSearchAPI:
    """Search and retrieve articles via the Scopus Search API"""

    _PAGE_TWO_INDEX = 1

    def __init__(
        self,
        http_client: HTTPClient,
        url_builder: URLBuilder,
        survey_details: SurveyDetails,
        state: SurveyState,
    ) -> None:
        """Search and retrieve articles via the Scopus Search API"""
        self._http_client = http_client
        self._url_builder = url_builder
        self._details = survey_details
        self._state = state
        self._last_completed: ResponseBundle = None

    @property
    def http_client(self) -> HTTPClient:
        return self._http_client

    async def _get_article(
        self, url: str, index: int
    ) -> tuple[ResponseBundle, int, ScopusPage]:
        res = await self._http_client.api_call(url)
        search = await asyncio.to_thread(validate_search_response, res)
        return res, index, search

    async def survey_totals_found(
        self, bundles_map: dict[int, CombinationBundle]
    ) -> list[Json]:
        tasks: list[asyncio.Task[tuple[ResponseBundle, int, ScopusPage]]] = []

        try:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(self._get_article(bundle.url, index))
                    for index, bundle in bundles_map.items()
                ]
        except ExceptionGroup:  # pylint: disable=W0718
            pass

        finally:
            await self._http_client.close()

        if not tasks:
            raise InternalError(ExcMsg.INTERNAL_ERROR)

        last_completed: ResponseBundle = None

        with progress_bar(len(bundles_map)) as pbar:
            for task in tasks:
                try:
                    last_completed, index, search = task.result()
                    bundles_map[index].total = search.total_results
                    pbar.step()

                except HTTPError as exc:
                    print("A")
                    raise exc

                except (asyncio.CancelledError, Exception) as exc:
                    print("B")
                    raise InternalError(ExcMsg.CANCELLED_ERROR, exc) from exc

        self._details.set_search_quota(last_completed)

        return [bundle.model_dump() for bundle in bundles_map.values()]

    async def _get_by_pagination(
        self, index: int
    ) -> tuple[ResponseBundle, ScopusPage]:
        page = index * self._state.items_per_page
        url = self._url_builder.pagination_url(page)

        res = await self._http_client.api_call(url)
        search = await asyncio.to_thread(validate_search_response, res)

        return res, search

    async def _get_multiple_articles_by_pagination(self) -> None:
        tasks: list[asyncio.Task[tuple[ResponseBundle, ScopusPage]]] = []

        try:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(self._get_by_pagination(start))
                    for start in self._state.pages_to_fetch_range
                ]
        except ExceptionGroup:  # pylint: disable=W0718
            pass

        if not tasks:
            raise InternalError(ExcMsg.INTERNAL_ERROR)

        last_completed: ResponseBundle = None

        with progress_bar(*self._state.pages_to_fetch_progress) as pbar:
            for task in tasks:
                try:
                    last_completed, search = task.result()
                    self._state.entry.extend(search.entry)
                    pbar.step()

                except HTTPError as exc:
                    raise exc

                except (asyncio.CancelledError, Exception) as exc:
                    raise InternalError(ExcMsg.CANCELLED_ERROR, exc) from exc

        self._details.set_search_quota(last_completed)

    async def search_articles(self, params: SurveyParams) -> None:
        url = self._url_builder.search_url(params)

        res = await self._http_client.api_call(url)
        search_results = validate_search_response(res)

        self._details.set_search_data(search_results)
        self._details.set_search_quota(res)

        self._state.set_first_search(search_results)

        if self._state.pages_count > 1:
            self._state.handle_search_quota(self._details.search_quota)

            if self._state.pages_count == 2:
                page = self._PAGE_TWO_INDEX * self._state.items_per_page
                url = self._url_builder.pagination_url(page)

                res = await self._http_client.api_call(url)
                self._details.set_search_quota(res)

                search_results = validate_search_response(res)
                self._state.entry.extend(search_results.entry)

            elif self._state.pages_count > 2:
                await self._get_multiple_articles_by_pagination()

        logger.total_found(self._state.total_results)

        self._state.validate_integrity()
