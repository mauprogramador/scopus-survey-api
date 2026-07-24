# mypy: disable-error-code="index"
import math
from unittest.mock import MagicMock

from httpx import AsyncClient as Client
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.adapters.gateway.scopus_dataset_gatherer import ScopusDatasetGatherer
from src.adapters.helpers.context import ScopusContext
from src.core.config.scopus import MAX_ITEMS_PER_PAGE, QUOTA_ERROR_CODE
from src.core.data.enums import ExcMsg
from tests.conftest import assert_error_json
from tests.mocks.errors import SCOPUS_API_QUOTA_ERROR
from tests.mocks.helpers import fqn, get_patch, load_csv_from_response, trans
from tests.mocks.integration import (
    ABSTRACT_QUOTA_EXCEEDED,
    EXACT_QUOTA_MORE_ABSTRACTS,
    EXACT_QUOTA_MORE_PAGES,
    EXACT_QUOTA_MORE_RESULTS,
    EXACT_QUOTA_ONE_ABSTRACT,
    EXACT_QUOTA_ONE_PAGE,
    EXACT_QUOTA_ONE_RESULT,
    EXACT_QUOTA_TWO_ABSTRACTS,
    EXACT_QUOTA_TWO_PAGES,
    EXACT_QUOTA_TWO_RESULTS,
    MORE_PAGES_FULL_ABSTRACTS,
    MORE_PARTIAL_PAGES_ABSTRACTS,
    NO_QUOTA_MORE_ABSTRACTS,
    NO_QUOTA_MORE_PAGES,
    NO_QUOTA_MORE_RESULTS,
    NO_QUOTA_TWO_ABSTRACTS,
    NO_QUOTA_TWO_PAGES,
    NO_QUOTA_TWO_RESULTS,
    ONE_PAGE_FULL_ABSTRACTS,
    ONE_PAGE_ONE_ABSTRACT,
    ONE_PAGE_TWO_ABSTRACTS,
    SEARCH_NOT_FOUND,
    SEARCH_QUOTA_EXCEEDED,
    TWO_PAGES_FULL_ABSTRACTS,
    TWO_PARTIAL_PAGES_ABSTRACTS,
)
from tests.mocks.raw import (
    HTTP_200,
    HTTP_404,
    HTTP_429,
    HTTP_502,
    SEARCH_PARAMS,
    URL_SEARCH,
)


CONTEXT = fqn(ScopusDatasetGatherer, ScopusContext)


@mark.asyncio
async def test_gather_one_page_one_abstract(mocker: Mocker, client: Client):
    ctx = ScopusContext()
    mocker.patch(CONTEXT, return_value=ctx)
    mock = mocker.patch(*get_patch(ONE_PAGE_ONE_ABSTRACT))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 2
    df = load_csv_from_response(res)
    assert df.shape[0] == len(ctx.abstracts) == 1
    assert len(ctx.entry) == 1 and ctx.items_per_page == 1
    assert ctx.total_results == 1 and ctx.pages_count == 1


@mark.asyncio
async def test_gather_one_page_two_abstracts(mocker: Mocker, client: Client):
    ctx = ScopusContext()
    mocker.patch(CONTEXT, return_value=ctx)
    mock = mocker.patch(*get_patch(ONE_PAGE_TWO_ABSTRACTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 3
    df = load_csv_from_response(res)
    assert df.shape[0] == 1 and len(ctx.abstracts) == 2
    assert len(ctx.entry) == 2 and ctx.items_per_page == 2
    assert ctx.total_results == 2 and ctx.pages_count == 1


@mark.asyncio
async def test_gather_one_page_full_abstracts(mocker: Mocker, client: Client):
    ctx = ScopusContext()
    mocker.patch(CONTEXT, return_value=ctx)
    mock = mocker.patch(*get_patch(ONE_PAGE_FULL_ABSTRACTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 26
    df = load_csv_from_response(res)
    assert df.shape[0] == 1 and len(ctx.abstracts) == 25
    assert len(ctx.entry) == 25 and ctx.items_per_page == 25
    assert ctx.total_results == 25 and ctx.pages_count == 1


@mark.asyncio
async def test_gather_two_pages_partial_abstracts(
    mocker: Mocker, client: Client
):
    ctx = ScopusContext()
    mocker.patch(CONTEXT, return_value=ctx)
    mock = mocker.patch(*get_patch(TWO_PARTIAL_PAGES_ABSTRACTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 32
    df = load_csv_from_response(res)
    assert df.shape[0] == 1 and len(ctx.abstracts) == 30
    assert len(ctx.entry) == 30 and ctx.items_per_page == 25
    assert ctx.total_results == 30 and ctx.pages_count == 2


@mark.asyncio
async def test_gather_two_pages_full_abstracts(mocker: Mocker, client: Client):
    ctx = ScopusContext()
    mocker.patch(CONTEXT, return_value=ctx)
    mock = mocker.patch(*get_patch(TWO_PAGES_FULL_ABSTRACTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    assert res.status_code == HTTP_200 and mock.call_count == 52
    df = load_csv_from_response(res)
    assert df.shape[0] == 1 and len(ctx.abstracts) == 50
    assert len(ctx.entry) == 50 and ctx.items_per_page == 25
    assert ctx.total_results == 50 and ctx.pages_count == 2


@mark.asyncio
async def test_gather_more_pages_partial_abstracts(
    mocker: Mocker, client: Client
):
    ctx = ScopusContext()
    mocker.patch(CONTEXT, return_value=ctx)
    mock = mocker.patch(*get_patch(MORE_PARTIAL_PAGES_ABSTRACTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 158
    df = load_csv_from_response(res)
    assert df.shape[0] == 1 and len(ctx.abstracts) == 151
    assert len(ctx.entry) == 151 and ctx.items_per_page == 25
    assert ctx.total_results == 151 and ctx.pages_count == 7


@mark.asyncio
async def test_gather_more_pages_full_abstracts(
    mocker: Mocker, client: Client
):
    ctx = ScopusContext()
    mocker.patch(CONTEXT, return_value=ctx)
    mock = mocker.patch(*get_patch(MORE_PAGES_FULL_ABSTRACTS))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    assert res.status_code == HTTP_200 and mock.call_count == 182
    df = load_csv_from_response(res)
    assert df.shape[0] == 1 and len(ctx.abstracts) == 175
    assert len(ctx.entry) == 175 and ctx.items_per_page == 25
    assert ctx.total_results == 175 and ctx.pages_count == 7


@mark.asyncio
async def test_gather_not_found(mocker: Mocker, client: Client):
    ctx = ScopusContext()
    mocker.patch(CONTEXT, return_value=ctx)
    mock = mocker.patch(*get_patch(SEARCH_NOT_FOUND))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    details = assert_error_json(res, HTTP_404, ExcMsg.ARTICLES_NOT_FOUND)
    print(details)
    assert mock.call_count == 1 and len(ctx.abstracts) == 0
    assert len(ctx.entry) == 0 and ctx.items_per_page == 0
    assert not ctx.total_results and ctx.pages_count == 0


@mark.asyncio
@mark.parametrize(
    "res_mock,total,has_search_quota,has_abstract_quota",
    [
        (EXACT_QUOTA_ONE_ABSTRACT, 1, True, False),
        (EXACT_QUOTA_ONE_PAGE, 1, False, True),
        (EXACT_QUOTA_ONE_RESULT, 1, False, False),
        (EXACT_QUOTA_TWO_ABSTRACTS, 2, True, False),
        (EXACT_QUOTA_TWO_PAGES, 26, False, True),
        (EXACT_QUOTA_TWO_RESULTS, 26, False, False),
        (EXACT_QUOTA_MORE_ABSTRACTS, 151, True, False),
        (EXACT_QUOTA_MORE_PAGES, 151, False, True),
        (EXACT_QUOTA_MORE_RESULTS, 151, False, False),
    ],
    ids=[
        "One abstract",
        "One page",
        "One result",
        "Two abstracts",
        "Two pages",
        "Two results",
        "More abstracts",
        "More pages",
        "More results",
    ],
)
async def test_gather_exact_quota_limit(  # pylint: disable=R0913,R0917
    mocker: Mocker,
    client: Client,
    res_mock: list[MagicMock],
    total: int,
    has_search_quota: bool,
    has_abstract_quota: bool,
):
    ctx = ScopusContext()
    mocker.patch(CONTEXT, return_value=ctx)

    mock = mocker.patch(*get_patch(res_mock))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    count = math.ceil(total / MAX_ITEMS_PER_PAGE)
    per_page = min(total, MAX_ITEMS_PER_PAGE)

    assert res.status_code == HTTP_200 and mock.call_count == len(res_mock)
    df = load_csv_from_response(res)
    assert df.shape[0] == 1 and len(ctx.abstracts) == total
    assert len(ctx.entry) == total and ctx.items_per_page == per_page
    assert ctx.total_results == total and ctx.pages_count == count

    if has_search_quota:
        assert int(res.headers["X-Search-Remaining"]) > 0
    else:
        assert int(res.headers["X-Search-Remaining"]) == 0

    if has_abstract_quota:
        assert int(res.headers["X-Abstract-Remaining"]) > 0
    else:
        assert int(res.headers["X-Abstract-Remaining"]) == 0


@mark.asyncio
@mark.parametrize(
    "res_mock,total,entry,has_search_quota,has_abstract_quota",
    [
        (NO_QUOTA_TWO_ABSTRACTS, 1, 2, True, False),
        (NO_QUOTA_TWO_PAGES, 25, 25, False, True),
        (NO_QUOTA_TWO_RESULTS, 1, 25, False, False),
        (NO_QUOTA_MORE_ABSTRACTS, 4, 7, True, False),
        (NO_QUOTA_MORE_PAGES, 100, 100, False, True),
        (NO_QUOTA_MORE_RESULTS, 100, 100, False, False),
    ],
    ids=[
        "Two abstracts",
        "Two pages",
        "Two results",
        "More abstracts",
        "More pages",
        "More results",
    ],
)
async def test_gather_insufficient_quota(  # pylint: disable=R0913,R0917
    mocker: Mocker,
    client: Client,
    res_mock: list[MagicMock],
    entry: int,
    total: int,
    has_search_quota: bool,
    has_abstract_quota: bool,
):
    ctx = ScopusContext()
    mocker.patch(CONTEXT, return_value=ctx)

    mock = mocker.patch(*get_patch(res_mock))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)

    count = math.ceil(entry / MAX_ITEMS_PER_PAGE)
    per_page = min(entry, MAX_ITEMS_PER_PAGE)

    assert res.status_code == HTTP_200 and mock.call_count == len(res_mock)
    df = load_csv_from_response(res)
    assert df.shape[0] == 1 and len(ctx.abstracts) == total
    assert len(ctx.entry) == entry and ctx.items_per_page == per_page
    assert ctx.total_results == total and ctx.pages_count == count

    if has_search_quota:
        assert int(res.headers["X-Search-Remaining"]) > 0
    else:
        assert int(res.headers["X-Search-Remaining"]) == 0

    if has_abstract_quota:
        assert int(res.headers["X-Abstract-Remaining"]) > 0
    else:
        assert int(res.headers["X-Abstract-Remaining"]) == 0


@mark.asyncio
async def test_gather_search_quota_exceeded(mocker: Mocker, client: Client):
    ctx = ScopusContext()
    mocker.patch(CONTEXT, return_value=ctx)
    mock = mocker.patch(*get_patch(SEARCH_QUOTA_EXCEEDED))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    details = assert_error_json(res, HTTP_502, trans(SCOPUS_API_QUOTA_ERROR))
    assert details is not None and mock.call_count == 1
    assert details[0]["status_code"] == HTTP_429
    assert details[0]["error_code"] == QUOTA_ERROR_CODE
    assert mock.call_count == 1 and len(ctx.abstracts) == 0
    assert len(ctx.entry) == 0 and not ctx.total_results
    assert not ctx.search_headers and not ctx.abstract_headers


@mark.asyncio
async def test_gather_abstract_quota_exceeded(mocker: Mocker, client: Client):
    ctx = ScopusContext()
    mocker.patch(CONTEXT, return_value=ctx)
    mock = mocker.patch(*get_patch(ABSTRACT_QUOTA_EXCEEDED))
    res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
    details = assert_error_json(res, HTTP_502, trans(SCOPUS_API_QUOTA_ERROR))
    assert details is not None and mock.call_count == 2
    assert details[0]["status_code"] == HTTP_429
    assert details[0]["error_code"] == QUOTA_ERROR_CODE
    assert mock.call_count == 2 and len(ctx.abstracts) == 0
    assert len(ctx.entry) == 1 and ctx.total_results == 1
    assert ctx.search_headers and not ctx.abstract_headers
