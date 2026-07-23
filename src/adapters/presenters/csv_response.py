from http import HTTPStatus

from fastapi.responses import FileResponse

from src.core.common.types import Headers
from src.core.config.config import DIRECTORY, FILE
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import NotFound


def csv_response(
    filename: str,
    api_key: str,
    headers: Headers,
) -> FileResponse:
    file_path = DIRECTORY / f"{api_key}_{FILE}"

    headers = {
        "X-CSV-Filename": filename,
        "X-API-Key": api_key,
    }
    headers.update(details_headers)

    return FileResponse(
        path=file_path,
        status_code=HTTPStatus.OK,
        headers=headers,
        media_type="text/csv",
        filename=filename,
    )


def retrieve_csv(api_key: str) -> FileResponse:
    filename = f"{api_key}_{FILE}"
    file_path = DIRECTORY / filename

    if not file_path.exists():
        raise NotFound(ExcMsg.CSV_NOT_FOUND)

    headers = {
        "X-CSV-Filename": filename,
        "X-API-Key": api_key,
    }

    return FileResponse(
        path=file_path,
        status_code=HTTPStatus.OK,
        headers=headers,
        media_type="text/csv",
        filename=filename,
    )
