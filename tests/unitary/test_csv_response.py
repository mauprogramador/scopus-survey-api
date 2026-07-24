from pytest import fixture, raises

from src.adapters.presenters.csv_response import csv_response, retrieve_csv
from src.adapters.serializers.query_params import SurveyParams
from src.core.domain.enums import ExcMsg
from src.core.domain.exceptions import NotFound
from src.infra.config.config import FILE
from tests.conftest import assert_http_error
from tests.mocks.raw import (
    API_KEY,
    CSV_FILE_NAME,
    DIRECTORY,
    HTTP_200,
    HTTP_404,
)


@fixture(scope="function", name="file")
def file_path_fixture():
    filename = f"any_{FILE}"
    file_path = DIRECTORY / filename
    file_path.touch()
    yield file_path, filename
    file_path.unlink(missing_ok=False)


def test_build_response():
    file_path = DIRECTORY / CSV_FILE_NAME
    res = csv_response(CSV_FILE_NAME, API_KEY, {"X-any": "any"})
    assert res.status_code == HTTP_200
    assert res.media_type == "text/csv"
    assert res.path == file_path and res.filename == CSV_FILE_NAME

    assert "attachment; filename" in res.headers["Content-Disposition"]
    assert "text/csv" in res.headers["Content-Type"]
    assert res.headers["X-CSV-Filename"] == CSV_FILE_NAME
    assert res.headers["X-API-Key"] == API_KEY
    assert res.headers["X-any"]


def test_retrieve_csv():
    file_path = DIRECTORY / CSV_FILE_NAME
    res = retrieve_csv(API_KEY)
    assert res.status_code == HTTP_200
    assert res.media_type == "text/csv"
    assert res.path == file_path and res.filename == CSV_FILE_NAME

    assert "attachment; filename" in res.headers["Content-Disposition"]
    assert "text/csv" in res.headers["Content-Type"]
    assert res.headers["X-CSV-Filename"] == CSV_FILE_NAME
    assert res.headers["X-API-Key"] == API_KEY


def test_csv_not_found():
    with raises(NotFound) as info:
        retrieve_csv("any")
    assert_http_error(info, HTTP_404, ExcMsg.CSV_NOT_FOUND)
    assert info.value.details is None
