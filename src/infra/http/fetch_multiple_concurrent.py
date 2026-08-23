import asyncio
import time
from collections.abc import Callable
from typing import Any

from src.adapters.serializers.scopus_data import ScopusHeaders
from src.adapters.types import Headers
from src.core.domain.types import ExcMsg
from src.infra.exceptions import TasksCancellationError
from src.infra.types import FetcherTask
from src.infra.utils import logger
from src.infra.utils.progress_bar import progress_bar


class _FetchMultiple[U]:

    def __init__(self, fetcher: Callable[..., FetcherTask[U]]) -> None:
        self._fetcher = fetcher
        self._results: list[U] = []
        self._headers: Headers = None

    async def _worker(
        self,
        args: int | tuple[int, Any],
        pbar_step: Callable[..., None],
    ) -> None:
        try:
            result, self._headers = await self._fetcher(args)
            self._results.append(result)
            pbar_step()

        except asyncio.CancelledError as exc:
            logger.error("Worker task was cancelled")
            logger.exception(exc)
            raise TasksCancellationError(ExcMsg.INTERNAL_ERROR, exc) from exc

    async def run(
        self,
        params: range | enumerate,
        progress: range,
    ) -> tuple[list[U], ScopusHeaders]:
        logger.batch_to_fetch(progress)
        start_time = time.perf_counter()

        with progress_bar(progress) as pbar_step:
            try:
                async with asyncio.TaskGroup() as tg:
                    for args in params:
                        tg.create_task(self._worker(args, pbar_step))

            except ExceptionGroup as exc_gp:
                logger.error(exc_gp.message)
                logger.exception(exc_gp)

                # Propagate the first caught error instead
                raise exc_gp.exceptions[0]

        if not self._results:
            raise TasksCancellationError(ExcMsg.INTERNAL_ERROR)

        process_time = time.perf_counter() - start_time
        logger.batch_completed(process_time)

        quota_headers = ScopusHeaders.model_validate(self._headers)

        return self._results, quota_headers


async def fetch_multiple[V](
    fetcher: Callable[..., FetcherTask[V]],
    params: range | enumerate,
    progress: range,
) -> tuple[list[V], ScopusHeaders]:
    return await _FetchMultiple(fetcher).run(params, progress)
