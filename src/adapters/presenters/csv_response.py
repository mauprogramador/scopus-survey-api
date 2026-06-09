from http import HTTPStatus

from fastapi.responses import FileResponse

from src.core.config.config import DIRECTORY, FILE
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import NotFound


def csv_response(
    filename: str, api_key: str, details_headers: dict[str, str]
) -> FileResponse:
    file_path = DIRECTORY / f"{api_key}_{FILE}"

    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": "text/csv; charset=utf-8",
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
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": "text/csv; charset=utf-8",
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
