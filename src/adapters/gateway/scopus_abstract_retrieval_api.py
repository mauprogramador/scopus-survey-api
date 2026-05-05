from asyncio import (
    CancelledError,
    as_completed,
    create_task,
    gather,
    get_running_loop,
)
from concurrent.futures import ThreadPoolExecutor
from os import cpu_count, sched_getaffinity

from pandas import DataFrame

from src.adapters.helpers.scopus_response import ScopusResponse
from src.core.common.error_messages import CANCELLED_ERROR
from src.core.common.types import ResponseBundle
from src.core.config.config import LOG
from src.core.domain.http_exceptions import HTTPError, ServiceUnavailable
from src.core.domain.protocols import (
    HTTPClient,
    QuotaResultsHandler,
    SurveyDetails,
    URLBuilder,
)
from src.utils.progress_bar import ProgressBar


class ScopusAbstractRetrievalAPI:
    """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""

    _ONE_RESULT_INDEX = 0
    _TWO_RESULTS_INDEX = 1
    _FIRST_ABSTRACT = 1

    def __init__(
        self,
        http_client: HTTPClient,
        url_builder: URLBuilder,
        survey_details: SurveyDetails,
    ) -> None:
        """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""
        self._http_client = http_client
        self._url_builder = url_builder
        self._details = survey_details
        self._state: QuotaResultsHandler = None

        try:
            self._workers = min(2 * len(sched_getaffinity(0)), 32)
        except AttributeError:
            self._workers = min(2 * (cpu_count() or 4), 32)

    async def _get_abstract(self, index: int) -> ResponseBundle:
        url = self._url_builder.abstract_url(self._state.entry[index].url)
        return await self._http_client.request(url)

    async def _get_multiple_abstracts(self) -> None:
        total = self._state.total_abstracts - self._FIRST_ABSTRACT
        max_workers = min(total, self._workers)
        LOG.debug({"max_workers": max_workers})

        all_tasks = {
            create_task(
                self._get_abstract(index),
                name=f"entry_index:{index}",
            )
            for index in range(total)
        }
        remaining_tasks = all_tasks.copy()
        last_completed: ResponseBundle = None

        with (
            ThreadPoolExecutor(max_workers) as executor,
            ProgressBar.start(total) as progress,
        ):
            for future in as_completed(all_tasks):
                remaining_tasks.discard(future)

                try:
                    response = await future
                    last_completed = response

                    abstract = await get_running_loop().run_in_executor(
                        executor,
                        ScopusResponse.validate_abstract,
                        response,
                    )
                    abstract_data = abstract.model_dump(by_alias=True)
                    self._state.abstracts.append(abstract_data)
                    progress.step()

                except (CancelledError, HTTPError, Exception) as exc:

                    for task in remaining_tasks:
                        if not task.done():
                            task.cancel()

                    if isinstance(exc, HTTPError):
                        raise exc

                    raise ServiceUnavailable(CANCELLED_ERROR, exc) from exc

        if remaining_tasks:
            await gather(*remaining_tasks, return_exceptions=True)

        self._details.set_abstract_quota(last_completed)

    async def _get_one_abstract(self, index: int) -> None:
        url = self._state.entry[index].url
        url = self._url_builder.abstract_url(url)

        response = await self._http_client.request(url)
        self._details.set_abstract_quota(response)

        abstract = ScopusResponse.validate_abstract(response)
        abstract_data = abstract.model_dump(by_alias=True)
        self._state.abstracts.append(abstract_data)

    async def retrieve_abstracts(
        self, api_key: str, state: QuotaResultsHandler
    ) -> DataFrame:
        self._state = state
        self._url_builder.set_abstract_query(api_key)
        self._state.fix_total()

        try:
            await self._get_one_abstract(self._ONE_RESULT_INDEX)

            if self._state.total_abstracts > 1:
                self._state.handle_abstract_quota(self._details.abstract_quota)

                if self._state.total_abstracts == 2:
                    await self._get_one_abstract(self._TWO_RESULTS_INDEX)

                elif self._state.total_abstracts > 2:
                    await self._http_client.update_strategy(
                        self._state.total_abstracts
                    )
                    await self._get_multiple_abstracts()
        finally:
            await self._http_client.close()

        self._details.set_results(self._state.total_abstracts)
        return DataFrame(self._state.abstracts)
