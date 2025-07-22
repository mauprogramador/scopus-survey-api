from http import HTTPStatus

from fastapi.responses import FileResponse

from src.core.common.error_messages import CSV_NOT_FOUND
from src.core.config.config import DIRECTORY, FILE
from src.core.domain.http_exceptions import NotFound


class CSVResponse:
    """Generates CSV file responses"""

    __MEDIA_TYPE = "text/csv"

    @classmethod
    def build(
        cls,
        api_key: str,
        headers: dict[str, str] | None = None,
    ) -> FileResponse:
        filename = f"{api_key}_{FILE}"
        file_path = DIRECTORY / filename

        if not file_path.exists():
            raise NotFound(CSV_NOT_FOUND)

        base_headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8",
            "X-CSV-Filename": filename,
            "X-API-Key": api_key,
        }

        if headers:
            base_headers.update(headers)

        return FileResponse(
            path=file_path,
            status_code=HTTPStatus.OK,
            headers=base_headers,
            media_type=cls.__MEDIA_TYPE,
            filename=filename,
        )
