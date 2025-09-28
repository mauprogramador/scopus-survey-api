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
from src.core.common.types import Json, ResponseBundle
from src.core.config.config import LOG
from src.core.data.serializers import ScopusEntry
from src.core.domain.http_exceptions import HTTPError, ServiceUnavailable
from src.core.domain.protocols import HTTPClient, SurveyDetails, URLBuilder
from src.utils.progress_bar import ProgressBar


class ScopusAbstractRetrievalAPI:
    """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""

    _ONE_RESULT_INDEX = 0

    def __init__(
        self,
        http_retry: HTTPClient,
        url_builder: URLBuilder,
        survey_detail: SurveyDetails,
    ) -> None:
        """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""
        self._http_retry = http_retry
        self._url_builder = url_builder
        self._survey_detail = survey_detail
        self._entry: list[ScopusEntry] = None
        self._abstracts: list[Json] = None
        self._total = 0

        try:
            self._workers = min(2 * len(sched_getaffinity(0)), 32)
        except AttributeError:
            self._workers = min(2 * (cpu_count() or 4), 32)

    async def _get_abstract(self, index: int) -> ResponseBundle:
        url = self._url_builder.abstract_url(self._entry[index].url)
        return await self._http_retry.request(url)

    async def _get_multiple_abstracts(self) -> None:
        max_workers = min(self._total, self._workers)
        LOG.debug({"max_workers": max_workers})

        all_tasks = {
            create_task(
                self._get_abstract(index),
                name=f"entry_index:{index}",
            )
            for index in range(self._total)
        }
        remaining_tasks = all_tasks.copy()
        last_completed: ResponseBundle = None

        with (
            ThreadPoolExecutor(max_workers) as executor,
            ProgressBar(self._total) as progress_bar,
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
                    self._abstracts.append(abstract_data)
                    progress_bar.step()

                except (CancelledError, HTTPError, Exception) as exc:

                    for task in remaining_tasks:
                        if not task.done():
                            task.cancel()

                    if isinstance(exc, HTTPError):
                        raise exc

                    raise ServiceUnavailable(CANCELLED_ERROR, exc) from exc

        if remaining_tasks:
            await gather(*remaining_tasks, return_exceptions=True)

        self._survey_detail.set_abstract_quota(last_completed)

    async def retrieve_abstracts(
        self, api_key: str, entry: list[ScopusEntry]
    ) -> DataFrame:
        self._abstracts = []
        self._entry, self._total = entry, len(entry)
        self._url_builder.set_abstract_query(api_key)

        try:
            if self._total == 1:
                url = self._entry[self._ONE_RESULT_INDEX].url
                url = self._url_builder.abstract_url(url)

                response = await self._http_retry.request(url)
                self._survey_detail.set_abstract_quota(response)

                abstract = ScopusResponse.validate_abstract(response)
                self._abstracts.append(abstract.model_dump(by_alias=True))

            else:
                await self._http_retry.update_strategy(self._total)
                await self._get_multiple_abstracts()
        finally:
            await self._http_retry.close()

        return DataFrame(self._abstracts)
