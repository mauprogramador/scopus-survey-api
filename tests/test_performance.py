import random
import string
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
from src.core.domain.types import Lang
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
from tests.mocks.models import ReportTracker
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


@mark.parametrize(
    "total,duration",
    [
        (100, (0.001, 0.001, 0.001, 0.001, 0.002, 0.001, 0.002)),
        (500, (0.001, 0.003, 0.001, 0.001, 0.001, 0.001, 0.002)),
        (1000, (0.001, 0.005, 0.002, 0.001, 0.001, 0.001, 0.003)),
        (2000, (0.002, 0.009, 0.003, 0.002, 0.002, 0.001, 0.005)),
        (5000, (0.003, 0.024, 0.006, 0.003, 0.002, 0.001, 0.097)),
        (10000, (0.006, 0.075, 0.010, 0.005, 0.002, 0.001, 0.020)),
    ],
    ids=["100", "500", "1.000", "2.000", "5.000", "10.000"],
)
def test_high_volume_data_parsing(total: int, duration: tuple[float, ...]):
    tracker = ReportTracker()

    pages_count = int(total / MAX_ITEMS_PER_PAGE)
    raw_list = [search_raw(total)] * pages_count
    assert len(raw_list) == pages_count

    with tracker.timeit(duration[0], "Parse ScopusPage"):
        for raw in raw_list:
            ScopusPage(**raw)

    raw_list = [abstract_raw()] * total
    assert len(raw_list) == total

    with tracker.timeit(duration[1], "Parse ScopusAbstract"):
        models = [ScopusAbstract(**raw) for raw in raw_list]
        assert len(models) == total

    with tracker.timeit(duration[2], "Dump ScopusAbstract"):
        raw_list = [model.model_dump(by_alias=True) for model in models]
        assert len(raw_list) == total

    with tracker.timeit(duration[3], "Build DataFrame"):
        df = pd.DataFrame(raw_list)
        assert df.shape[0] == total

    with tracker.timeit(duration[4], "Parse DateTime"):
        # pylint: disable=W0212
        df_subset = df.loc[:, SimilarityFilter._COLUMNS].copy()
        assert df.shape[0] == total

        pd.to_datetime(
            df_subset["date"],
            yearfirst=True,
            format="%Y-%m-%d",  # e.g. 2026-01-01
            errors="coerce",
        )

    with tracker.timeit(duration[5], "Renaming columns"):
        df = df.rename(columns=_COLUMN_TRANSLATION)
        assert df.shape[0] == total

    file_path = DIRECTORY / f"test_{FILE}"

    with tracker.timeit(duration[6], "Write CSV"):
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
        (10, 0.004),
        (30, 0.004),
        (50, 0.005),
        (70, 0.008),
        (100, 0.013),
        (150, 0.024),
    ],
    ids=["10", "30", "50", "70", "100", "150"],
)
def test_high_volume_filtering_one_group(total: int, duration: float):
    tracker = ReportTracker()

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
        (100, 0.008),
        (500, 0.0270),
        (1000, 0.050),
        (2000, 0.100),
        (5000, 0.250),
        (10000, 0.500),
    ],
    ids=["100", "500", "1.000", "2.000", "5.000", "10.000"],
)
def test_high_volume_filtering_groups(total: int, duration: float):
    tracker = ReportTracker()
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
        (100, 0.009),
        (500, 0.003),
        (1000, 0.003),
        (2000, 0.003),
        (5000, 0.004),
        (10000, 0.005),
    ],
    ids=["100", "500", "1.000", "2.000", "5.000", "10.000"],
)
@mark.asyncio
async def test_high_volume_csv_download(
    total: int, duration: float, mocker: Mocker, client: Client
):
    tracker = ReportTracker()
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
    [(0.014, Lang.EN_US), (0.010, Lang.PT_BR)],
    ids=["Web Form [en-US]", "Web Form [pt-BR]"],
)
@mark.asyncio
async def test_web_form_route_process_time(
    duration: float, lang: Lang, mocker: Mocker, client: Client
):
    mocker.stopall()
    tracker = ReportTracker()

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
    [(0.160, 3, 2), (0.200, 7, 3), (1.000, 15, 4)],
    ids=["3 Combs", "7 Combs", "15 Combs"],
)
@mark.asyncio
async def test_api_combination_route_process_time(
    duration: float, count: int, index: int, mocker: Mocker, client: Client
):
    mocker.stopall()
    tracker = ReportTracker()

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
    tracker = ReportTracker()

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
    tracker = ReportTracker()

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
