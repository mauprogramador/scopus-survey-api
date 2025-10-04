from pathlib import Path

from pytest import fixture, raises

from src.adapters.presenters.csv_response import CSVResponse
from src.core.common.error_messages import CSV_NOT_FOUND
from src.core.config.config import DIRECTORY, FILE
from src.core.domain.http_exceptions import NotFound
from tests.conftest import assert_http_error
from tests.mocks.raw import CSV_MEDIA, HTTP_200, HTTP_404


@fixture(scope="function", name="file")
def file_path_fixture():
    filename = f"any_{FILE}"
    file_path = DIRECTORY / filename

    with open(file_path, "w", encoding="utf-8"):
        pass

    yield file_path, filename

    file_path.unlink(missing_ok=False)


def test_build_response(file: tuple[Path, str]):
    response = CSVResponse.build(f"any_{FILE}", "any", {"X-any": "any"})
    assert response.status_code == HTTP_200
    assert response.media_type == CSV_MEDIA
    assert response.path == file[0] and response.filename == file[1]

    assert response.headers.get("Content-Disposition")
    assert response.headers.get("Content-Type")
    assert response.headers.get("X-CSV-Filename") == file[1]
    assert response.headers.get("X-API-Key") == "any"
    assert response.headers.get("X-any") == "any"


def test_retrieve_csv(file: tuple[Path, str]):
    response = CSVResponse.retrieve("any")
    assert response.status_code == HTTP_200
    assert response.media_type == CSV_MEDIA
    assert response.path == file[0] and response.filename == file[1]

    assert response.headers.get("Content-Disposition")
    assert response.headers.get("Content-Type")
    assert response.headers.get("X-CSV-Filename") == file[1]
    assert response.headers.get("X-API-Key") == "any"


def test_csv_not_found():
    with raises(NotFound) as info:
        CSVResponse.retrieve("any")
    assert_http_error(info, HTTP_404, CSV_NOT_FOUND)
    assert info.value.errors is None
