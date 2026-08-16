import contextlib
import cProfile
import io
import pstats
import random
import re
import shutil
import string
import time
import tracemalloc
from typing import cast
from unittest.mock import MagicMock

import pandas as pd
from httpx import AsyncClient as Client
from pytest import FixtureRequest, Mark, fixture, mark, skip
from pytest_mock import MockerFixture as Mocker

from src.adapters.persistence.csv_builder import (
    _COLUMN_TRANSLATION,
    write_csv_file,
)
from src.adapters.serializers.query_params import SurveyParams
from src.adapters.serializers.scopus_data import ScopusAbstract, ScopusPage
from src.core.domain.types import Json, Lang
from src.core.use_cases.similarity_filter import SimilarityFilter
from src.infra.config.config import DIRECTORY, FILE
from src.infra.config.scopus import MAX_ITEMS_PER_PAGE
from tests.mocks.helpers import (
    abstract_raw,
    get_patch,
    load_csv_from_response,
    response_mock,
    search_raw,
)
from tests.mocks.raw import (
    ALIAS_SEARCH_PARAMS,
    COMBINATION_PARAMS,
    CSV_PARAMS,
    DETAILS,
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
_REASON = "Performance tests must be run individually to ensure clean metrics"


@fixture(autouse=True, scope="function")
def enforce_performance_isolation(request: FixtureRequest):
    if request.session.testscollected == 1:
        return

    if request.session.testscollected > 7:
        skip(_REASON)

    parametrize_mark = cast(Mark | None, request.keywords.get("parametrize"))

    if not parametrize_mark:
        skip(_REASON)

    names = {item.name.rsplit("[", 1)[0] for item in request.session.items}

    if len(names) > 1:
        skip(_REASON)


class _ReportTracker:
    _NOTE = "[{}] Duration ({:.4f}s) exceeded limit ({:.4f}s)"
    # e.g. 45 function calls
    _INDENT_PATTERN = re.compile(r"\n? *(\d* function calls)")
    _FILTER = (tracemalloc.Filter(True, "/src"),)
    _TOP = 15  # Top bottlenecks functions
    _TOLERANCE = 0.30  # 30%

    def __init__(self) -> None:
        self._metrics: list[Json] = []
        self._profiler: cProfile.Profile | None = None
        self._snapshot: tracemalloc.Snapshot | None = None
        self._peak_bytes: float | None = None

    @contextlib.contextmanager
    def timeit(self, expected_time: float, op_name: str):
        time_limit = expected_time * (1 + self._TOLERANCE)
        half_limit = time_limit / 2.0

        start_time = time.perf_counter()
        yield
        elapsed = time.perf_counter() - start_time

        if elapsed > time_limit:
            status = "FAILED (Too Slow)"
        elif elapsed < half_limit:
            status = "OPPORTUNITY (Fast)"
        else:
            status = "PASSED"

        report = {
            "Operation": op_name,
            "Elapsed (s)": round(elapsed, 4),
            "Target (s)": round(expected_time, 4),
            "Limit (s)": round(time_limit, 4),
            "Status": status,
        }
        self._metrics.append(report)

        note = self._NOTE.format(op_name, elapsed, time_limit)
        assert elapsed <= time_limit, note

    @contextlib.contextmanager
    def measure(self):
        if self._profiler is None:
            self._profiler = cProfile.Profile()

        tracemalloc.start()
        self._profiler.enable()

        try:
            yield
        finally:
            self._profiler.disable()

        self._snapshot = tracemalloc.take_snapshot()
        _, peak_bytes = tracemalloc.get_traced_memory()

        tracemalloc.stop()
        self._peak_bytes = round(peak_bytes / (1024 * 1024), 2)

    def _header(self, title: str, lib: str) -> None:
        print(f"\n\033[37;1m{title}\033[m (\033[36m{lib}\033[m)\n")

    def show_report(self):
        width = shutil.get_terminal_size(fallback=(80, 24)).columns
        print()
        print(" \033[93mReport\033[m ".center((width + 8), "-"))
        self._header("Operational Metrics", "time.perf_counter")

        df = pd.DataFrame(self._metrics)
        print(df.to_string(index=False))

        if not self._profiler and not self._snapshot:
            print()

        if self._profiler is not None:
            buffer = io.StringIO()
            stats = pstats.Stats(self._profiler, stream=buffer)

            stats.sort_stats("cumulative")
            stats.print_stats("/src", self._TOP)

            stats.sort_stats("tottime")
            stats.print_stats("/src", self._TOP)

            self._header(f"Top {self._TOP} CPU Bottlenecks", "cProfile")
            value = buffer.getvalue().strip()
            print(self._INDENT_PATTERN.sub(r"   \1", value))

        if self._snapshot is not None:
            self._header(f"Top {self._TOP} Memory Allocations", "tracemalloc")
            total = len(self._snapshot.statistics("lineno"))

            snapshot = self._snapshot.filter_traces(self._FILTER)
            stats = snapshot.statistics("lineno")

            print(
                f"List reduced from {total} to {len(stats)} "
                "due to restriction <'/src'>\n"
            )

            for stat in stats[: self._TOP]:
                print(
                    f"{stat.traceback[0]}: {stat.size / 1024:.1f} "
                    f"KiB ({stat.count} blocks)"
                )

            print()
            other = stats[self._TOP :]

            if other:
                size = sum(stat.size for stat in other)
                print(f"Other {len(other)} process: {(size / 1024):.1f} KiB")

            total = sum(stat.size for stat in stats)
            print(f"Total Allocated Size: {(total / 1024):.1f} KiB")

            if self._peak_bytes is not None:
                print(f"Peak Memory: {self._peak_bytes} MB\n")


@mark.parametrize(
    "total,duration",
    [
        (100, 0.01),
        (500, 0.01),
        (1000, 0.01),
        (2000, 0.02),
        (5000, 0.04),
        (10000, 0.11),
    ],
    ids=["100", "500", "1.000", "2.000", "5.000", "10.000"],
)
def test_high_volume_data_parsing(total: int, duration: float):
    tracker = _ReportTracker()

    pages_count = int(total / MAX_ITEMS_PER_PAGE)
    raw_list = [search_raw(total)] * pages_count
    assert len(raw_list) == pages_count

    with tracker.timeit(duration, "Parse ScopusPage"):
        for raw in raw_list:
            ScopusPage(**raw)

    raw_list = [abstract_raw()] * total
    assert len(raw_list) == total

    with tracker.timeit(duration, "Parse ScopusAbstract"):
        models = [ScopusAbstract(**raw) for raw in raw_list]
        assert len(models) == total

    with tracker.timeit(duration, "Dump ScopusAbstract"):
        raw_list = [model.model_dump(by_alias=True) for model in models]
        assert len(raw_list) == total

    with tracker.timeit(duration, "Build DataFrame"):
        df = pd.DataFrame(raw_list)
        assert df.shape[0] == total

    with tracker.timeit(duration, "Parse DateTime"):
        # pylint: disable=W0212
        df_subset = df.loc[:, SimilarityFilter._COLUMNS].copy()
        assert df.shape[0] == total

        pd.to_datetime(
            df_subset["date"],
            yearfirst=True,
            format="%Y-%m-%d",  # e.g. 2026-01-01
            errors="coerce",
        )

    with tracker.timeit(duration, "Renaming columns"):
        df = df.rename(columns=_COLUMN_TRANSLATION)
        assert df.shape[0] == total

    file_path = DIRECTORY / f"test_{FILE}"

    with tracker.timeit(duration, "Write CSV"):
        with file_path.open(mode="w", encoding="utf-8") as file:
            df.to_csv(
                file,
                sep=";",
                header=True,
                index=False,
                encoding="utf-8",
            )

    file_path.unlink()
    tracker.show_report()


@mark.parametrize(
    "total,duration",
    [
        (10, 0.01),
        (30, 0.01),
        (50, 0.01),
        (70, 0.01),
        (100, 0.01),
        (150, 0.02),
    ],
    ids=["10", "30", "50", "70", "100", "150"],
)
def test_high_volume_filtering_one_group(total: int, duration: float):
    tracker = _ReportTracker()

    df = pd.DataFrame(
        {
            "authors": ["any_authors"] * total,
            "title": [f"any_title_{index + 1}" for index in range(total)],
            "date": [*["2026-01-01"] * (total - 1), "2026-01-02"],
        }
    )
    assert df.shape[0] == total

    with tracker.timeit(duration, "Filter one group"):
        df = SimilarityFilter().filter(df, 80)  # default ratio

    with tracker.measure():
        df = SimilarityFilter().filter(df, 80)  # default ratio

    assert df.shape[0] == 1 and df["date"].iloc[0] == "2026-01-02"
    tracker.show_report()


@mark.parametrize(
    "total,duration",
    [
        (100, 0.01),
        (500, 0.03),
        (1000, 0.05),
        (2000, 0.08),
        (5000, 0.20),
        (10000, 0.50),
    ],
    ids=["100", "500", "1.000", "2.000", "5.000", "10.000"],
)
def test_high_volume_filtering_groups(total: int, duration: float):
    tracker = _ReportTracker()
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

    with tracker.timeit(duration, "Filter groups"):
        df = SimilarityFilter().filter(df, 80)  # default ratio

    with tracker.measure():
        df = SimilarityFilter().filter(df, 80)  # default ratio

    assert df.shape[0] == ngroups

    for row in df["date"]:
        assert row == "2026-01-02"

    tracker.show_report()


@mark.parametrize(
    "total,duration",
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
    total: int, duration: float, mocker: Mocker, client: Client
):
    tracker = _ReportTracker()
    mocker.stopall()

    data = ScopusAbstract(**abstract_raw()).model_dump(by_alias=True)
    df = pd.DataFrame([data] * total)
    assert df.shape[0] == total

    write_csv_file(df, SurveyParams(**ALIAS_SEARCH_PARAMS), DETAILS)

    with tracker.timeit(duration, "CSV Download"):
        res = await client.get(URL_CSV, params=CSV_PARAMS)
        assert res.status_code == HTTP_200

    with tracker.measure():
        res = await client.get(URL_CSV, params=CSV_PARAMS)
        assert res.status_code == HTTP_200

    tracker.show_report()


@mark.parametrize(
    "duration,lang",
    [(0.02, Lang.EN_US), (0.02, Lang.PT_BR)],
    ids=["Web Form [en-US]", "Web Form [pt-BR]"],
)
@mark.asyncio
async def test_web_form_route_process_time(
    duration: float, lang: Lang, mocker: Mocker, client: Client
):
    mocker.stopall()
    tracker = _ReportTracker()

    client.cookies.clear()
    client.headers.clear()

    with tracker.timeit(duration, f"Web Form [{lang.value}]"):
        res = await client.get(URL_WEB.replace(Lang.EN_US, lang))
        assert res.status_code == HTTP_200

    with tracker.measure():
        res = await client.get(URL_WEB.replace(Lang.EN_US, lang))
        assert res.status_code == HTTP_200

    tracker.show_report()


@mark.parametrize(
    "duration,count,index",
    [(0.20, 3, 2), (0.20, 7, 3), (1.00, 15, 4)],
    ids=["3 Combs", "7 Combs", "15 Combs"],
)
@mark.asyncio
async def test_api_combination_route_process_time(
    duration: float, count: int, index: int, mocker: Mocker, client: Client
):
    mocker.stopall()
    tracker = _ReportTracker()

    mocker.patch.dict(COMBINATION_PARAMS, {"keywords": KEYWORDS[:index]})
    mock = mocker.patch(*get_patch([response_mock(RAW_SEARCH_OK)] * count))

    with tracker.timeit(duration, f"Survey {count} Combinations"):
        res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
        assert res.status_code == HTTP_200 and mock.call_count == count

    mocker.stop(mock)
    mock = mocker.patch(*get_patch([response_mock(RAW_SEARCH_OK)] * count))

    with tracker.measure():
        res = await client.get(URL_COMBINATION, params=COMBINATION_PARAMS)
        assert res.status_code == HTTP_200 and mock.call_count == count

    tracker.show_report()


@mark.parametrize(
    "duration,count,op_name,res_mock",
    [
        (
            0.31,
            2,
            "Survey One Result",
            [
                response_mock(RAW_SEARCH_OK),
                response_mock(RAW_ABSTRACT_OK),
            ],
        ),
        (
            2.44,
            26,
            "Survey One Page Full",
            [
                response_mock(search_raw(25)),
                *[response_mock(RAW_ABSTRACT_OK)] * 25,
            ],
        ),
    ],
    ids=["One Result", "One Page Full"],
)
@mark.asyncio
async def test_api_survey_route_process_time(  # pylint: disable=R0913,R0917
    duration: float,
    count: int,
    op_name: str,
    res_mock: list[MagicMock],
    mocker: Mocker,
    client: Client,
):
    mocker.stopall()
    tracker = _ReportTracker()

    mock = mocker.patch(*get_patch(res_mock))

    with tracker.timeit(duration, op_name):
        res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
        assert res.status_code == HTTP_200 and mock.call_count == count

    mocker.stop(mock)
    mock = mocker.patch(*get_patch(res_mock))

    with tracker.measure():
        res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
        assert res.status_code == HTTP_200 and mock.call_count == count

    tracker.show_report()


@mark.asyncio
async def test_high_volume_complete_survey(mocker: Mocker, client: Client):
    mocker.stopall()
    tracker = _ReportTracker()

    data = [
        response_mock(search_raw(50)),
        response_mock(
            abstract_raw(
                "any_title",
                "".join(random.choices(string.ascii_letters, k=12)),
                "2026-01-01",
            )
        ),
        response_mock(search_raw(50)),
    ]
    unique = [
        response_mock(
            abstract_raw(
                "any_title",
                "".join(random.choices(string.ascii_letters, k=12)),
                "2026-01-01",
            )
        )
        for _ in range(24)
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

    with tracker.timeit(5.72, "Complete Survey"):
        res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
        assert res.status_code == HTTP_200 and mock.call_count == 52

    mocker.stop(mock)
    mock = mocker.patch(*get_patch(data))

    with tracker.measure():
        res = await client.get(URL_SEARCH, params=SEARCH_PARAMS)
        assert res.status_code == HTTP_200 and mock.call_count == 52

    assert mock.call_count == 52
    df = load_csv_from_response(res)
    assert df.shape[0] == 30  # 25 unique + 1 per group

    tracker.show_report()
