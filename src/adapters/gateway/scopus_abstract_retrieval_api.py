import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from pandas import DataFrame

from src.adapters.helpers.scopus_response import validate_abstract_response
from src.core.common.types import (
    HTTPClient,
    QuotaResultsHandler,
    ResponseBundle,
    SurveyDetails,
    URLBuilder,
)
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import HTTPError, InternalError
from src.utils.progress_bar import ProgressBar


class ScopusAbstractRetrievalAPI:
    """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""

    _ONE_RESULT_INDEX = 0
    _TWO_RESULTS_INDEX = 1

    def __init__(
        self,
        http_client: HTTPClient,
        url_builder: URLBuilder,
        survey_details: SurveyDetails,
        state: QuotaResultsHandler,
    ) -> None:
        """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""
        self._http_client = http_client
        self._url_builder = url_builder
        self._details = survey_details
        self._state = state

        try:
            self._workers = min(2 * len(os.sched_getaffinity(0)), 32)
        except AttributeError:
            self._workers = min(2 * (os.cpu_count() or 4), 32)

    async def _get_abstract(self, index: int) -> ResponseBundle:
        url = self._url_builder.abstract_url(self._state.entry[index].url)
        return await self._http_client.request(url)

    async def _get_multiple_abstracts(self) -> None:
        max_workers = min(self._state.abstracts_to_fetch, self._workers)
        logger.debug({"max_workers": max_workers})

        all_tasks = {
            asyncio.create_task(
                self._get_abstract(index),
                name=f"entry_index:{index}",
            )
            for index in self._state.abstracts_to_fetch_range
        }
        remaining_tasks = all_tasks.copy()
        last_completed: ResponseBundle = None

        with (
            ThreadPoolExecutor(max_workers) as executor,
            ProgressBar.start(self._state.abstracts_to_fetch) as progress,
        ):
            for future in asyncio.as_completed(all_tasks):
                remaining_tasks.discard(future)

                try:
                    res = await future
                    last_completed = res

                    abstract = (
                        await asyncio.get_running_loop().run_in_executor(
                            executor,
                            validate_abstract_response,
                            res,
                        )
                    )
                    abstract_data = abstract.model_dump(by_alias=True)
                    self._state.abstracts.append(abstract_data)
                    progress.step()

                except (asyncio.CancelledError, HTTPError, Exception) as exc:

                    for task in remaining_tasks:
                        if task.done() and not isinstance(
                            exc, asyncio.CancelledError
                        ):
                            task.exception()  # Retrieve task exception
                        else:
                            task.cancel()

                    if isinstance(exc, HTTPError):
                        raise exc

                    raise ServiceUnavailable(
                        ExcMsg.CANCELLED_ERROR, exc
                    ) from exc

        if remaining_tasks:
            await asyncio.gather(*remaining_tasks, return_exceptions=True)

        self._details.set_abstract_quota(last_completed)

    async def _get_one_abstract(self, index: int) -> None:
        url = self._state.entry[index].url
        url = self._url_builder.abstract_url(url)

        res = await self._http_client.request(url)
        self._details.set_abstract_quota(res)

        abstract = validate_abstract_response(res)
        abstract_data = abstract.model_dump(by_alias=True)
        self._state.abstracts.append(abstract_data)

    async def retrieve_abstracts(self, api_key: str) -> DataFrame:
        self._url_builder.set_abstract_query(api_key)
        self._state.fix_total()

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

        self._details.set_results(self._state.total_abstracts)
        return DataFrame(self._state.abstracts)
