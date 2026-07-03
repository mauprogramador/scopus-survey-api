import contextlib
import random
import string
import time

import pandas as pd
from httpx import AsyncClient as Client
from pytest import mark, param
from pytest_mock import MockerFixture as Mocker

from src.core.config.config import DIRECTORY, FILE
from src.core.config.scopus import MAX_ITEMS_PER_PAGE
from src.core.data.csv_builder import _COLUMN_TRANSLATION, write_csv_file
from src.core.data.enums import Button, Lang
from src.core.data.query_params import SurveyParams
from src.core.data.serializers import ScopusAbstract, ScopusPage
from src.core.use_cases.similarity_filter import SimilarityFilter
from tests.mocks.helpers import (
    abstract_raw,
    get_patch,
    load_csv_from_response,
    response_mock,
    search_raw,
)
from tests.mocks.raw import (
    ALIAS_SEARCH_PARAMS,
    API_KEY,
    CSV_PARAMS,
    HTTP_200,
    KEYWORDS,
    RAW_ABSTRACT_OK,
    RAW_SEARCH_OK,
    SEARCH_PARAMS,
    URL_COMBINATION,
    URL_CSV,
    URL_SEARCH,
    URL_WEB,
)


# Base duration is the P95 time based on a summary report of 50x executions


@contextlib.contextmanager
def _assert_time(elapsed: float):
    start_time = time.perf_counter()
    yield
    duration = time.perf_counter() - start_time
    latency = elapsed * (1 + 0.30)  # 30% tolerance
    assert duration <= latency


@mark.parametrize(
    "total,elapsed",
    [
        (100, 0.01),
        (500, 0.01),
        (1000, 0.01),
        param(2000, 0.02, marks=mark.xfail(reason="Unstable latency")),
        param(5000, 0.04, marks=mark.xfail(reason="Unstable latency")),
        param(10000, 0.11, marks=mark.xfail(reason="Unstable latency")),
    ],
    ids=["100", "500", "1.000", "2.000", "5.000", "10.000"],
)
def test_high_volume_data_parsing(total: int, elapsed: float):
    pages_count = int(total / MAX_ITEMS_PER_PAGE)
    raw_list = [search_raw(total)] * pages_count
    assert len(raw_list) == pages_count

    with _assert_time(elapsed):
        for raw in raw_list:
            ScopusPage(**raw)

    raw_list = [abstract_raw()] * total
    assert len(raw_list) == total

    with _assert_time(elapsed):
        models = [ScopusAbstract(**raw) for raw in raw_list]
        assert len(models) == total

    with _assert_time(elapsed):
        raw_list = [model.model_dump(by_alias=True) for model in models]
        assert len(raw_list) == total

    with _assert_time(elapsed):
        df = pd.DataFrame(raw_list)
        assert df.shape[0] == total

    with _assert_time(elapsed):
        # pylint: disable=W0212
        df_subset = df.loc[:, SimilarityFilter._COLUMNS].copy()
        assert df.shape[0] == total

        pd.to_datetime(
            df_subset["date"],
            yearfirst=True,
            format="%Y-%m-%d",  # e.g. 2026-01-01
            errors="coerce",
        )

    with _assert_time(elapsed):
        df = df.rename(columns=_COLUMN_TRANSLATION)
        assert df.shape[0] == total

    file_path = DIRECTORY / f"test_{FILE}"

    with _assert_time(elapsed):
        with file_path.open(mode="w", encoding="utf-8") as file:
            df.to_csv(
                file,
                sep=";",
                header=True,
                index=False,
                encoding="utf-8",
            )

    file_path.unlink()


@mark.parametrize(
    "total,elapsed",
    [
        (10, 0.01),
        (30, 0.01),
        (50, 0.01),
        (70, 0.01),
        (100, 0.01),
        (150, 0.01),
    ],
    ids=["10", "30", "50", "70", "100", "150"],
)
def test_high_volume_filtering_one_group(total: int, elapsed: float):
    df = pd.DataFrame(
        {
            "authors": ["any_authors"] * total,
            "title": [f"any_title_{index + 1}" for index in range(total)],
            "date": [*["2026-01-01"] * (total - 1), "2026-01-02"],
        }
    )
    assert df.shape[0] == total

    with _assert_time(elapsed):
        df = SimilarityFilter().filter(df, 80)  # default ratio

    assert df.shape[0] == 1 and df["date"].iloc[0] == "2026-01-02"


@mark.parametrize(
    "total,elapsed",
    [
        (100, 0.01),
        (500, 0.01),
        (1000, 0.02),
        (2000, 0.04),
        (5000, 0.08),
        (10000, 0.16),
    ],
    ids=["100", "500", "1.000", "2.000", "5.000", "10.000"],
)
def test_high_volume_filtering_groups(total: int, elapsed: float):
    data, ngroups = [], int(total / 50)  # 50doc per group

    for _ in range(ngroups):
        author = "".join(random.choices(string.ascii_letters, k=12))

        for index in range(1, 51):
            group = {
                "authors": author,
                "title": f"any_title_{index:02d}",
                "date": "2026-01-01",
            }
            data.append(group)

        data[-1]["date"] = "2026-01-02"

    df = pd.DataFrame(data)
    assert df.shape[0] == total

    with _assert_time(elapsed):
        df = SimilarityFilter().filter(df, 80)  # default ratio

    assert df.shape[0] == ngroups

    for row in df["date"]:
        assert row == "2026-01-02"


@mark.parametrize(
    "total,elapsed",
    [
        (100, 0.01),
        (500, 0.01),
        (1000, 0.01),
        (2000, 0.01),
        (5000, 0.01),
        (10000, 0.01),
    ],
    ids=["100", "500", "1.000", "2.000", "5.000", "10.000"],
)
@mark.asyncio
async def test_high_volume_csv_download(
    total: int, elapsed: float, mocker: Mocker, client: Client
):
    mocker.stopall()

    data = ScopusAbstract(**abstract_raw()).model_dump(by_alias=True)
    df = pd.DataFrame([data] * total)
    assert df.shape[0] == total

    write_csv_file(df, SurveyParams(**ALIAS_SEARCH_PARAMS), ["any"])

    with _assert_time(elapsed):
        res = await client.get(URL_CSV, params=CSV_PARAMS)
        assert res.status_code == HTTP_200


@mark.asyncio
async def test_web_form_route_process_time(mocker: Mocker, client: Client):
    mocker.stopall()
    client.cookies.clear()
    client.headers.clear()

    with _assert_time(0.02):
        res = await client.get(URL_WEB)
        assert res.status_code == HTTP_200

    client.cookies.clear()

    with _assert_time(0.02):
        res = await client.get(URL_WEB.replace(Lang.EN_US, Lang.PT_BR))
        assert res.status_code == HTTP_200


@mark.asyncio
async def test_api_combination_route_process_time(
    mocker: Mocker, client: Client
):
    mocker.stopall()
    mock = mocker.patch(*get_patch([response_mock(RAW_SEARCH_OK)] * 3))
    params = {
        "apiKey": API_KEY,
        "keywords": KEYWORDS[:2],
        "button": Button.COMBINATION.value,
    }

    with _assert_time(0.20):
        res = await client.get(URL_COMBINATION, params=params)
        assert res.status_code == HTTP_200 and mock.call_count == 3

    mocker.stop(mock)
    mock = mocker.patch(*get_patch([response_mock(RAW_SEARCH_OK)] * 7))
    params["keywords"] = KEYWORDS[:3]

    with _assert_time(0.20):
        res = await client.get(URL_COMBINATION, params=params)
        assert res.status_code == HTTP_200 and mock.call_count == 7

    mocker.stop(mock)
    mock = mocker.patch(*get_patch([response_mock(RAW_SEARCH_OK)] * 15))
    params["keywords"] = KEYWORDS

    with _assert_time(1.00):
        res = await client.get(URL_COMBINATION, params=params)
        assert res.status_code == HTTP_200 and mock.call_count == 15


@mark.asyncio
async def test_api_survey_route_process_time(mocker: Mocker, client: Client):
    mocker.stopall()
    res_mock = [response_mock(RAW_SEARCH_OK), response_mock(RAW_ABSTRACT_OK)]
    mock = mocker.patch(*get_patch(res_mock))
    params = {
        "apiKey": API_KEY,
        "keywords": KEYWORDS[:2],
        "combination": "any",
        "button": Button.SURVEY.value,
    }

    with _assert_time(0.31):
        res = await client.get(URL_SEARCH, params=params)
        assert res.status_code == HTTP_200 and mock.call_count == 2

    mocker.stop(mock)
    res_mock = [
        response_mock(search_raw(25)),
        *[response_mock(RAW_ABSTRACT_OK)] * 25,
    ]
    mock = mocker.patch(*get_patch(res_mock))

    with _assert_time(2.44):
        res = await client.get(URL_SEARCH, params=params)
        assert res.status_code == HTTP_200 and mock.call_count == 26


@mark.asyncio
async def test_high_volume_complete_survey(mocker: Mocker, client: Client):
    mocker.stopall()

    data = [response_mock(search_raw(50))] * 2
    unique = [
        response_mock(
            abstract_raw(
                "any_title",
                "".join(random.choices(string.ascii_letters, k=12)),
                "2026-01-01",
            )
        )
        for _ in range(25)
    ]
    data.extend(unique)

    for _ in range(5):
        author = "".join(random.choices(string.ascii_letters, k=12))
        group = [
            response_mock(
                abstract_raw(f"any_title_{index}", author, "2026-01-01")
            )
            for index in range(1, 6)
        ]
        assert len(group) == 5
        data.extend(group)

    assert len(data) == 52  # 2 full pages + 50 abstracts
    mock = mocker.patch(*get_patch(data))

    with _assert_time(5.72):
        res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
        assert res.status_code == HTTP_200

    assert mock.call_count == 52
    df = load_csv_from_response(res)
    assert df.shape[0] == 30  # 25 unique + 1 per group
