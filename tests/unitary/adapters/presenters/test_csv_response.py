from pathlib import Path

from pytest import fixture, raises

from src.adapters.presenters.csv_response import CSVResponse
from src.core.common.messages import CSV_NOT_FOUND
from src.core.config.config import DIRECTORY, FILE
from src.core.domain.http_exceptions import NotFound
from tests.conftest import assert_http_error


@fixture(scope="module", name="file")
def file_path_fixture():
    filename = f"any_{FILE}"
    file_path = DIRECTORY / filename

    with open(file_path, "w", encoding="utf-8"):
        pass

    yield file_path, filename

    file_path.unlink(missing_ok=True)


def test_csv_response(file: tuple[Path, str]):
    response = CSVResponse.build("any")
    assert response.status_code == 200 and response.media_type == "text/csv"
    assert response.path == file[0] and response.filename == file[1]

    assert response.headers.get("Content-Disposition")
    assert response.headers.get("Content-Type")
    assert response.headers.get("X-CSV-Filename") == file[1]
    assert response.headers.get("X-API-Key") == "any"


def test_csv_response_headers(file: tuple[Path, str]):
    response = CSVResponse.build("any", {"X-any": "any"})
    assert response.status_code == 200 and response.media_type == "text/csv"
    assert response.path == file[0] and response.filename == file[1]

    assert response.headers.get("X-CSV-Filename") == file[1]
    assert response.headers.get("X-API-Key") == "any"
    assert response.headers.get("X-any") == "any"


def test_file_path_not_found():
    with raises(NotFound) as exc:
        CSVResponse.build("any")
    assert_http_error(exc, 404, CSV_NOT_FOUND, False)
