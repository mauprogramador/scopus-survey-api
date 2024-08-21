from pytest import raises
from pytest_mock import MockerFixture

from app.core.common.messages import INTERRUPT_ERROR
from app.core.config.scopus import NULL
from app.core.domain.exceptions import InterruptError
from tests.mocks import unitary as mock
from tests.mocks.fixtures import GET_ARTICLES_PAGE, IS_SET, PAGE_SCRAPER


def test_scrape(mocker: MockerFixture):
    mocker.patch(GET_ARTICLES_PAGE, return_value=mock.SUBSET_TEMPLATE)
    PAGE_SCRAPER.set_subset(mock.SUBSET_TEMPLATE)
    scrap_data = PAGE_SCRAPER.scrape(0)

    assert scrap_data.index == 0
    assert scrap_data.data == mock.SCRAP_DATA


def test_template_null(mocker: MockerFixture):
    mocker.patch(GET_ARTICLES_PAGE, return_value=mock.SUBSET_NULL)
    PAGE_SCRAPER.set_subset(mock.SUBSET_NULL)
    scrap_data = PAGE_SCRAPER.scrape(0)

    assert scrap_data.index == 0
    assert scrap_data.data == ["any", NULL, NULL]


def test_scrape_multiple(mocker: MockerFixture):
    mocker.patch(GET_ARTICLES_PAGE, return_value=mock.SUBSET_MULTIPLE)
    PAGE_SCRAPER.set_subset(mock.SUBSET_TEMPLATE)

    for index in range(mock.SUBSET_MULTIPLE.shape[0]):
        scrap_data = PAGE_SCRAPER.scrape(index)
        assert scrap_data.index == index

        if scrap_data.data[1] == NULL:
            assert scrap_data.data == ["any", NULL, NULL]
        else:
            assert scrap_data.data == mock.SCRAP_DATA


def test_interrupt_error(mocker: MockerFixture):
    mocker.patch(GET_ARTICLES_PAGE, return_value=mock.SUBSET_TEMPLATE)
    mocker.patch(IS_SET, return_value=True)
    PAGE_SCRAPER.set_subset(mock.SUBSET_TEMPLATE)

    with raises(InterruptError) as error:
        PAGE_SCRAPER.scrape(0)

    assert error.value.code == 500
    assert error.value.message == INTERRUPT_ERROR
