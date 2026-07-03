import asyncio

from pandas import DataFrame

from src.adapters.helpers.response_auditor import validate_abstract_response
from src.core.common.types import (
    HTTPClient,
    Json,
    ResponseBundle,
    SurveyDetails,
    SurveyState,
    URLBuilder,
)
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import HTTPError, InternalError
from src.utils.progress_bar import progress_bar


class ScopusAbstractRetrievalAPI:
    """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""

    _ONE_RESULT_INDEX = 0
    _TWO_RESULTS_INDEX = 1

    def __init__(
        self,
        http_client: HTTPClient,
        url_builder: URLBuilder,
        survey_details: SurveyDetails,
        state: SurveyState,
    ) -> None:
        """Retrieves Scopus abstracts via the Scopus Abstract Retrieval API"""
        self._http_client = http_client
        self._url_builder = url_builder
        self._details = survey_details
        self._state = state

    async def _get_abstract(self, index: int) -> tuple[ResponseBundle, Json]:
        url = self._url_builder.abstract_url(self._state.entry[index].url)

        res = await self._http_client.api_call(url)
        abstract = await asyncio.to_thread(validate_abstract_response, res)

        return res, abstract.model_dump(by_alias=True)

    async def _get_multiple_abstracts(self) -> None:
        tasks: list[asyncio.Task[tuple[ResponseBundle, Json]]] = []

        try:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(self._get_abstract(index))
                    for index in self._state.abstracts_to_fetch_range
                ]
        except ExceptionGroup:  # pylint: disable=W0718
            pass

        if not tasks:
            raise InternalError(ExcMsg.INTERNAL_ERROR)

        last_completed: ResponseBundle = None

        with progress_bar(self._state.abstracts_to_fetch) as pbar:
            for task in tasks:
                try:
                    last_completed, abstract_data = task.result()
                    self._state.abstracts.append(abstract_data)
                    pbar.step()

                except HTTPError as exc:
                    raise exc

                except (asyncio.CancelledError, Exception) as exc:
                    raise InternalError(ExcMsg.CANCELLED_ERROR, exc) from exc

        self._details.set_abstract_quota(last_completed)

    async def _get_one_abstract(self, index: int) -> None:
        url = self._url_builder.abstract_url(self._state.entry[index].url)
        res = await self._http_client.api_call(url)

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
                await self._get_multiple_abstracts()

        self._details.set_results(self._state.total_abstracts)
        return DataFrame(self._state.abstracts)
