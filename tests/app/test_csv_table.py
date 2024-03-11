from pandas import DataFrame
from pytest_mock import MockerFixture

from app.utils.csv_table import LoadCSVData
from tests.data import mocks


def test_handle_none():
    csv_data = LoadCSVData().handle()
    assert csv_data is None


def test_handle(mocker: MockerFixture):
    mocker.patch(mocks.READ_CSV, return_value=DataFrame(mocks.FAKE_CSV_DATA))
    csv_data = LoadCSVData().handle()
    assert csv_data == mocks.FAKE_CSV_DATA
