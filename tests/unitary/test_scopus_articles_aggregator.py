from pathlib import PosixPath
from unittest.mock import AsyncMock, MagicMock, Mock

from pandas import DataFrame, read_csv
from pytest import mark
from pytest_mock import MockerFixture as Mocker

from src.adapters.gateway.scopus_abstract_retrieval_api import (
    ScopusAbstractRetrievalAPI,
)
from src.adapters.gateway.scopus_search_api import ScopusSearchAPI
from src.core.config.scopus import FOOTNOTE
from src.core.data.query_params import SearchParams
from src.core.data.survey_detail import SurveyDetail
from src.core.use_cases.articles_similarity_filter import (
    ArticlesSimilarityFilter,
)
from src.core.use_cases.scopus_articles_aggregator import (
    ScopusArticlesAggregator,
)
from tests.mocks.helpers import mock_filter
from tests.mocks.raw import ALIAS_SEARCH_PARAMS, HTTP_200, LOG_DATA
from tests.mocks.unitary import (
    DIFFERENT_ARTICLES,
    EXACT_DUPLICATES,
    SAME_TITLE_AND_AUTHORS,
)

RETRIEVE_ABSTRACTS = AsyncMock()
FILTER = Mock(side_effect=mock_filter)
SET_LOSS = Mock()
ARTICLES_AGGREGATOR = ScopusArticlesAggregator(
    AsyncMock(spec=ScopusSearchAPI),
    AsyncMock(
        spec=ScopusAbstractRetrievalAPI,
        retrieve_abstracts=RETRIEVE_ABSTRACTS,
    ),
    MagicMock(spec=ArticlesSimilarityFilter, filter=FILTER),
    MagicMock(spec=SurveyDetail, log_data=LOG_DATA, set_loss=SET_LOSS),
)
PARAMS = SearchParams(**ALIAS_SEARCH_PARAMS)


@mark.asyncio
async def test_one_row(mocker: Mocker):
    RETRIEVE_ABSTRACTS.return_value = DIFFERENT_ARTICLES.iloc[0:1]
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_csv = mocker.spy(DataFrame, "to_csv")

    res = await ARTICLES_AGGREGATOR.retrieve_articles(PARAMS)
    df_spy: DataFrame = spy_csv.call_args_list[0].args[0]

    assert res.status_code == HTTP_200 and df_spy.shape == (1, 11)
    spy_drop.assert_not_called()
    FILTER.assert_not_called()
    SET_LOSS.assert_called_once_with(0, 0.0)


@mark.asyncio
async def test_more_rows(mocker: Mocker):
    RETRIEVE_ABSTRACTS.return_value = DIFFERENT_ARTICLES
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_csv = mocker.spy(DataFrame, "to_csv")

    res = await ARTICLES_AGGREGATOR.retrieve_articles(PARAMS)
    df_spy: DataFrame = spy_csv.call_args_list[0].args[0]

    assert res.status_code == HTTP_200 and df_spy.shape == (7, 11)
    spy_drop.assert_called()
    FILTER.assert_called()
    SET_LOSS.assert_called_with(0, 0.0)


@mark.asyncio
async def test_drop_exact_duplicates(mocker: Mocker):
    FILTER.reset_mock()
    RETRIEVE_ABSTRACTS.return_value = EXACT_DUPLICATES
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_reset = mocker.spy(DataFrame, "reset_index")

    res = await ARTICLES_AGGREGATOR.retrieve_articles(PARAMS)
    df_in: DataFrame = spy_drop.call_args_list[0].args[0]
    df_out: DataFrame = spy_reset.call_args_list[0].args[0]

    assert res.status_code == HTTP_200
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1

    FILTER.assert_not_called()
    SET_LOSS.assert_called_with(1, 50.0)


@mark.asyncio
async def test_drop_same_title_and_authors(mocker: Mocker):
    FILTER.reset_mock()
    RETRIEVE_ABSTRACTS.return_value = SAME_TITLE_AND_AUTHORS
    spy_drop = mocker.spy(DataFrame, "drop_duplicates")
    spy_reset = mocker.spy(DataFrame, "reset_index")

    res = await ARTICLES_AGGREGATOR.retrieve_articles(PARAMS)
    df_in: DataFrame = spy_drop.call_args_list[1].args[0]
    df_out: DataFrame = spy_reset.call_args_list[1].args[0]

    assert res.status_code == HTTP_200
    assert df_in.shape[0] == 2 and df_out.shape[0] == 1

    FILTER.assert_not_called()
    SET_LOSS.assert_called_with(1, 50.0)


@mark.asyncio
async def test_non_ratio(mocker: Mocker):
    FILTER.reset_mock()
    RETRIEVE_ABSTRACTS.return_value = DIFFERENT_ARTICLES
    PARAMS.ratio = 0

    spy = mocker.spy(DataFrame, "to_csv")
    res = await ARTICLES_AGGREGATOR.retrieve_articles(PARAMS)
    df_spy: DataFrame = spy.call_args_list[0].args[0]

    assert res.status_code == HTTP_200 and df_spy.shape == (7, 11)
    FILTER.assert_not_called()
    SET_LOSS.assert_called_with(0, 0.0)


@mark.asyncio
async def test_footnote(mocker: Mocker):
    RETRIEVE_ABSTRACTS.return_value = EXACT_DUPLICATES
    spy = mocker.spy(DataFrame, "to_csv")

    res = await ARTICLES_AGGREGATOR.retrieve_articles(PARAMS)
    df_spy: DataFrame = spy.call_args_list[0].args[0]
    file_path: PosixPath = spy.call_args_list[0].args[1]

    df = read_csv(
        filepath_or_buffer=file_path,
        header=0,
        sep=";",
        keep_default_na=False,
        encoding="utf-8",
    )

    assert res.status_code == HTTP_200 and df_spy.shape == (1, 11)
    assert df.shape == (2, 11)  # +1 footnote
    assert df.iloc[-1].iloc[0].startswith(FOOTNOTE[:41])
    assert df.iloc[-1].iloc[0].endswith(FOOTNOTE[-50:])
