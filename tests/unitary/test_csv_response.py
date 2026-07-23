from pytest import fixture, raises

from src.adapters.presenters.csv_response import csv_response, retrieve_csv
from src.core.config.config import FILE
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import NotFound
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
    assert res.media_type == CSV_MEDIA
    assert res.path == file[0] and res.filename == file[1]

    assert res.headers.get("Content-Disposition")
    assert res.headers.get("Content-Type")
    assert res.headers.get("X-CSV-Filename") == file[1]
    assert res.headers.get("X-API-Key") == "any"
    assert res.headers.get("X-any") == "any"


def test_retrieve_csv():
    file_path = DIRECTORY / CSV_FILE_NAME
    res = retrieve_csv(API_KEY)
    assert res.status_code == HTTP_200
    assert res.media_type == CSV_MEDIA
    assert res.path == file[0] and res.filename == file[1]

    assert res.headers.get("Content-Disposition")
    assert res.headers.get("Content-Type")
    assert res.headers.get("X-CSV-Filename") == file[1]
    assert res.headers.get("X-API-Key") == "any"


def test_csv_not_found():
    with raises(NotFound) as info:
        retrieve_csv("any")
    assert_http_error(info, HTTP_404, ExcMsg.CSV_NOT_FOUND)
    assert info.value.details is None
