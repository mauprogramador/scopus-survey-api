# mypy: disable-error-code="index"
import asyncio
import threading
from typing import Any

from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker
from slowapi.errors import RateLimitExceeded

from src.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from src.adapters.gateway.scopus_search_api import ScopusSearchAPI
from src.core.common.types import SurveyState
from src.core.data.enums import ExcMsg
from src.core.domain.factory import make_aggregator
from src.framework.fastapi.main import app
from src.framework.middleware.flow_guarding_monitor import (
    FlowGuardingMonitorMiddleware,
)
from tests.conftest import SEMAPHORE, assert_error_json
from tests.mocks.errors import RATE_LIMIT_ERROR
from tests.mocks.helpers import (
    MockSemaphore,
    fqn,
    get_patch,
    response_mock,
    search_raw,
    spec,
    trans,
)
from tests.mocks.integration import SURVEY_FOUR_KEYWORDS
from tests.mocks.raw import (
    COMBINATION_PARAMS,
    CSV_PARAMS,
    HTTP_200,
    HTTP_429,
    KEYWORDS,
    RAW_ABSTRACT_OK,
    RAW_SEARCH_OK,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_CSV,
    URL_SEARCH,
)


TO_THREAD = spec(ScopusSearchAPI, asyncio.to_thread, "asyncio")


def _task_name(task: asyncio.Task) -> str:
    if not task.get_name().startswith("Task-"):
        return task.get_name()
    coro = task.get_coro()
    return coro.__qualname__ if coro else task.get_name()


@mark.asyncio
async def test_slowapi_rate_limit_exceed(mocker: Mocker, client: Client):
    setattr(app.state.limiter, "enabled", True)
    mocker.stopall()

    async def _hit_endpoint():
        return await client.get(URL_CSV, params=CSV_PARAMS)

    tasks = [_hit_endpoint() for _ in range(70)]
    results = await asyncio.gather(*tasks)
    setattr(app.state.limiter, "enabled", False)

    status_codes = [res.status_code for res in results]
    assert status_codes.count(HTTP_200) == 60
    assert status_codes.count(HTTP_429) == 10

    res = results[status_codes.index(HTTP_429)]
    details = assert_error_json(res, HTTP_429, trans(RATE_LIMIT_ERROR))
    assert details[0]["type"] == fqn(RateLimitExceeded)
    assert details[0]["message"] == ExcMsg.SLOWAPI_RATE_ERROR
    assert details[0]["error"]["status_code"] == HTTP_429
    assert URL_CSV in details[0]["error"]["resource"]
    assert details[0]["error"]["rate"] == "60 per 2 second"


@mark.asyncio
async def test_async_tasks_api_combination(mocker: Mocker, client: Client):
    running_tasks: set[asyncio.Task[Any]] = set()

    def _retrieve_tasks(func, *args):
        loop = asyncio.get_running_loop()
        running_tasks.update(asyncio.all_tasks(loop))
        return func(*args)  # Call validate_search_response passing res

    mocker.patch(**TO_THREAD, side_effect=_retrieve_tasks)
    mock = mocker.patch(*get_patch([response_mock(RAW_SEARCH_OK)] * 3))

    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3

    assert len(running_tasks) == 6

    task_names = ":".join(_task_name(task) for task in running_tasks)
    # pylint: disable=W0212
    assert task_names.count(ScopusSearchAPI._get_article.__qualname__) == 3
    assert task_names.count(fqn(FlowGuardingMonitorMiddleware.__call__)) == 2
    assert task_names.count("test_async_tasks_api_combination") == 1


@mark.asyncio
async def test_async_tasks_api_survey(mocker: Mocker, client: Client):
    running_tasks: set[asyncio.Task[Any]] = set()

    def _retrieve_tasks(func, *args):
        loop = asyncio.get_running_loop()
        running_tasks.update(asyncio.all_tasks(loop))
        return func(*args)  # Call validate_search_response passing res

    ctx = ScopusContext()
    mocker.patch(CONTEXT, return_value=ctx)
    mocker.patch(**TO_THREAD, side_effect=_retrieve_tasks)
    mock = mocker.patch(
        *get_patch(
            [
                *[response_mock(search_raw(51, 1))] * 3,
                *[response_mock(RAW_ABSTRACT_OK)] * 3,
            ]
        )
    )

    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 6

    assert len(ctx.entry) == 3 and ctx.total_results == 3
    assert ctx.pages_count == 1 and len(running_tasks) == 5

    task_names = ":".join(_task_name(task) for task in running_tasks)

    # pylint: disable=W0212
    method = ScopusSearchAPI._get_by_pagination.__qualname__
    assert task_names.count(method) == 2

    # pylint: disable=W0212
    method = ScopusAbstractRetrievalAPI._get_abstract.__qualname__
    assert task_names.count(method) == 2

    assert task_names.count(fqn(FlowGuardingMonitorMiddleware.__call__)) == 2
    assert task_names.count("test_async_tasks_api_survey") == 1


@mark.asyncio
async def test_semaphore_queue_flow(mocker: Mocker, client: Client):
    mocker.stopall()
    mock = mocker.patch(*get_patch(SURVEY_FOUR_KEYWORDS))

    sem = MockSemaphore(5)
    mocker.patch(SEMAPHORE, return_value=sem)

    mocker.patch.dict(COMBINATION_PARAMS, {"keywords": KEYWORDS})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 15

    assert len(sem.acquires) == 15
    assert len(sem.releases) == 15

    assert all(sem.acquires[index]["waiters"] == 0 for index in range(6))
    assert any(
        snap["waiters"] > 0 for snap in sem.acquires if snap["value"] == 0
    )
    assert any(
        snap["value"] > 0 for snap in sem.releases if snap["waiters"] == 0
    )


@mark.asyncio
async def test_threading_offload(mocker: Mocker, client: Client):
    mock = mocker.patch(*get_patch(SURVEY_FOUR_KEYWORDS))

    mocker.patch.dict(COMBINATION_PARAMS, {"keywords": KEYWORDS})
    res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 15

    assert any(
        "ThreadPoolExecutor" in thread.name for thread in threading.enumerate()
    )
