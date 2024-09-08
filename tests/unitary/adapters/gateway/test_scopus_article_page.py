from pytest_mock import MockerFixture

from app.core.config.scopus import NULL, PAGE_COLUMN
from app.framework.exceptions import BadGateway, GatewayTimeout
from tests.mocks import common as data
from tests.mocks import unitary as mock
from tests.mocks.fixtures import ARTICLES_PAGE, REQUEST


def test_one_row(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.ANY_RESPONSE)
    result = ARTICLES_PAGE.get_articles_page(mock.ONE_ROW.copy())
    assert result is not None and result.shape == (1, 3)
    assert result.equals(mock.DF_OUT.iloc[0:1])


def test_two_rows(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ANY_PAGES[0:2])
    result = ARTICLES_PAGE.get_articles_page(mock.TWO_ROWS.copy())
    assert result is not None and result.shape == (2, 3)
    assert result.equals(mock.DF_OUT.iloc[0:2])


def test_more_rows(mocker: MockerFixture):
    mocker.patch(REQUEST, side_effect=mock.ANY_PAGES)
    result = ARTICLES_PAGE.get_articles_page(mock.DF_IN)
    assert result is not None and result.shape == (7, 3)
    assert result.equals(mock.DF_OUT)


def test_status_error(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.ERROR_RESPONSES[500])
    result = ARTICLES_PAGE.get_articles_page(mock.ONE_ROW.copy())
    assert result is not None and result.shape == (1, 3)
    assert result.loc[0, PAGE_COLUMN] == NULL


def test_empty_response(mocker: MockerFixture):
    mocker.patch(REQUEST, return_value=data.EMPTY_RESPONSE)
    result = ARTICLES_PAGE.get_articles_page(mock.ONE_ROW.copy())
    assert result is not None and result.shape == (1, 3)
    assert result.loc[0, PAGE_COLUMN] == NULL


def test_exceptions(mocker: MockerFixture):
    exceptions = [BadGateway("any"), GatewayTimeout("any")]
    mocker.patch(REQUEST, side_effect=exceptions)
    result = ARTICLES_PAGE.get_articles_page(mock.ONE_ROW.copy())
    assert result is not None and result.shape == (1, 3)
    assert result.loc[0, PAGE_COLUMN] == NULL


def test_second_chance(mocker: MockerFixture):
    side_effect = [GatewayTimeout("any"), data.ANY_RESPONSE]
    mocker.patch(REQUEST, side_effect=side_effect)
    result = ARTICLES_PAGE.get_articles_page(mock.ONE_ROW.copy())
    assert result is not None and result.shape == (1, 3)
    assert result.equals(mock.DF_OUT.iloc[0:1])
