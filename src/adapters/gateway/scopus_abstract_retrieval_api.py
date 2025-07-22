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
from src.core.domain.protocols import HTTPClient, SurveyDetail, URLBuilder
from src.utils.progress_bar import ProgressBar


class ScopusAbstractRetrievalAPI:
    """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""

    __ONE_RESULT_INDEX = 0

    def __init__(
        self,
        http_retry: HTTPClient,
        url_builder: URLBuilder,
        survey_detail: SurveyDetail,
    ) -> None:
        """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""
        self.__http_retry = http_retry
        self.__url_builder = url_builder
        self.__survey_detail = survey_detail
        self.__entry: list[ScopusEntry] = None
        self.__abstracts: list[Json] = []
        self.__total = 0

        try:
            self.__workers = min(2 * len(sched_getaffinity(0)), 32)
        except AttributeError:
            self.__workers = min(2 * (cpu_count() or 4), 32)

    async def __get_abstract(self, index: int) -> ResponseBundle:
        url = self.__url_builder.abstract_url(self.__entry[index].url)
        return await self.__http_retry.request(url)

    async def __get_multiple_abstracts(self) -> None:
        max_workers = min(self.__total, self.__workers)
        LOG.debug({"max_workers": max_workers})

        all_tasks = {
            create_task(
                self.__get_abstract(start),
                name=f"pagination_start:{start}",
            )
            for start in range(self.__total)
        }
        remaining_tasks = all_tasks.copy()
        last_completed: ResponseBundle = None

        with (
            ThreadPoolExecutor(max_workers) as executor,
            ProgressBar(self.__total) as progress_bar,
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
                    self.__abstracts.append(abstract_data)
                    progress_bar.step()

                except (CancelledError, Exception) as exc:
                    LOG.error(CANCELLED_ERROR)

                    for task in remaining_tasks:
                        if not task.done():
                            task.cancel()

                    raise exc

            if remaining_tasks:
                await gather(*remaining_tasks, return_exceptions=True)

        self.__survey_detail.set_quota_data(last_completed)

    async def retrieve_abstracts(
        self, api_key: str, entry: list[ScopusEntry]
    ) -> DataFrame:
        self.__entry, self.__total = entry, len(entry)
        self.__url_builder.set_abstract_query(api_key)

        try:
            if self.__total == 1:
                url = self.__entry[self.__ONE_RESULT_INDEX].url
                url = self.__url_builder.abstract_url(url)

                response = await self.__http_retry.request(url)
                self.__survey_detail.set_quota_data(response)

                abstract = ScopusResponse.validate_abstract(response)
                self.__abstracts.append(abstract.model_dump(by_alias=True))

            else:
                await self.__get_multiple_abstracts()
        finally:
            await self.__http_retry.close()

        return DataFrame(self.__abstracts)
