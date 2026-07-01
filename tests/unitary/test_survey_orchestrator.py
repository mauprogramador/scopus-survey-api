from pandas import DataFrame
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.core.data.csv_builder import write_csv_file
from src.core.data.query_params import SurveyParams
from src.core.use_cases.survey_orchestrator import SurveyOrchestrator
from tests.mocks.helpers import aggregator_fix, fqn
from tests.mocks.raw import ALIAS_SEARCH_PARAMS, HTTP_200
from tests.mocks.unitary import (
    DIFFERENT_ARTICLES,
    EXACT_DUPLICATES,
    SAME_TITLE_AND_AUTHORS,
)


PARAMS = SurveyParams(**ALIAS_SEARCH_PARAMS)
WRITE_CSV = fqn(SurveyOrchestrator, write_csv_file)


@mark.asyncio
async def test_one_row(mocker: Mocker):
    fix = aggregator_fix(DIFFERENT_ARTICLES.iloc[0:1])
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_write = mocker.patch(WRITE_CSV, wraps=write_csv_file)

    res = await fix.use_case.retrieve_articles(PARAMS)
    df_spy: DataFrame = spy_write.call_args_list[0].args[0]

    assert res.status_code == HTTP_200 and df_spy.shape == (1, 11)
    spy_drop.assert_not_called()
    fix.filter.assert_not_called()
    fix.set_loss.assert_called_once_with(0, 0.0)


@mark.asyncio
async def test_more_rows(mocker: Mocker):
    fix = aggregator_fix(DIFFERENT_ARTICLES)
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_write = mocker.patch(WRITE_CSV, wraps=write_csv_file)

    res = await fix.use_case.retrieve_articles(PARAMS)
    df_spy: DataFrame = spy_write.call_args_list[0].args[0]

    assert res.status_code == HTTP_200 and df_spy.shape == (7, 11)
    spy_drop.assert_called()
    fix.filter.assert_called()
    fix.set_loss.assert_called_with(0, 0.0)


@mark.asyncio
async def test_drop_exact_duplicates(mocker: Mocker):
    fix = aggregator_fix(EXACT_DUPLICATES)
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_reset = mocker.spy(DataFrame, "reset_index")

    res = await fix.use_case.retrieve_articles(PARAMS)
    df_in: DataFrame = spy_drop.call_args_list[0].args[0]
    df_out: DataFrame = spy_reset.call_args_list[0].args[0]

    assert res.status_code == HTTP_200
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1

    fix.filter.assert_not_called()
    fix.set_loss.assert_called_with(1, 50.0)


@mark.asyncio
async def test_drop_same_title_and_authors(mocker: Mocker):
    fix = aggregator_fix(SAME_TITLE_AND_AUTHORS)
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_reset = mocker.spy(DataFrame, "reset_index")

    res = await fix.use_case.retrieve_articles(PARAMS)
    df_in: DataFrame = spy_drop.call_args_list[1].args[0]
    df_out: DataFrame = spy_reset.call_args_list[1].args[0]

    assert res.status_code == HTTP_200
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1

    fix.filter.assert_not_called()
    fix.set_loss.assert_called_with(1, 50.0)


@mark.asyncio
async def test_non_ratio(mocker: Mocker):
    fix = aggregator_fix(DIFFERENT_ARTICLES)
    PARAMS.ratio = 0

    spy = mocker.patch(WRITE_CSV, wraps=write_csv_file)
    res = await fix.use_case.retrieve_articles(PARAMS)
    df_spy: DataFrame = spy.call_args_list[0].args[0]

    assert res.status_code == HTTP_200 and df_spy.shape == (7, 11)
    fix.filter.assert_not_called()
    fix.set_loss.assert_called_with(0, 0.0)
