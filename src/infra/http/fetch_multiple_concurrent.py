import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

from src.adapters.serializers.scopus_data import ScopusHeaders
from src.core.domain.enums import ExcMsg
from src.core.domain.exceptions import InternalError
from src.core.domain.types import Headers
from src.infra.utils import logger
from src.infra.utils.progress_bar import progress_bar


async def fetch_multiple[T](
    fetcher: Callable[..., Coroutine[Any, Any, tuple[T, Headers]]],
    params: range | enumerate,
    progress: range,
) -> tuple[list[T], ScopusHeaders]:
    tasks: list[asyncio.Task[tuple[T, Headers]]] = []

    try:
        with progress_bar(progress) as pbar_step:
            async with asyncio.TaskGroup() as tg:
                for args in params:
                    task = tg.create_task(fetcher(args))
                    task.add_done_callback(pbar_step)
                    tasks.append(task)

    except ExceptionGroup as exc_gp:
        logger.error(exc_gp.message)
        logger.exception(exc_gp)

        raise exc_gp.exceptions[0]

    if not tasks:
        raise InternalError(ExcMsg.INTERNAL_ERROR)

    quota_headers: Headers = None
    results: list[T] = []

    for task in tasks:
        result, quota_headers = task.result()
        results.append(result)

    return results, ScopusHeaders.model_validate(quota_headers)
