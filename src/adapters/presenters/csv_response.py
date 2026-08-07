from http import HTTPStatus

from fastapi.responses import FileResponse

from src.core.domain.exceptions import NotFound
from src.core.domain.types import ExcMsg, SurveyDetails, SurveyParams
from src.infra.config.config import DIRECTORY, FILE


def csv_response(
    filename: str,
    params: SurveyParams,
    details: SurveyDetails,
) -> FileResponse:
    file_path = DIRECTORY / f"{params.api_key}_{FILE}"

    headers = {
        "X-CSV-Filename": filename,
        "X-API-Key": params.api_key,
        "X-Combination": params.combination,
        "X-Scopus-Total": str(details.search_result.total_results),
        "X-Total-Retrieved": str(details.total_retrieved),
        "X-Total-Final": str(details.total_final),
        "X-Pages-Count": str(details.pages_count),
        "X-Items-Per-Page": str(details.search_result.items_per_page),
        "X-Search-Limit": str(details.search_headers.limit),
        "X-Search-Remaining": str(details.search_headers.remaining),
        "X-Search-Reset": str(details.search_headers.reset),
        "X-Abstract-Limit": str(details.abstract_headers.limit),
        "X-Abstract-Remaining": str(details.abstract_headers.remaining),
        "X-Abstract-Reset": str(details.abstract_headers.reset),
    }

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

    headers = {"X-CSV-Filename": filename, "X-API-Key": api_key}

    return FileResponse(
        path=file_path,
        status_code=HTTPStatus.OK,
        headers=headers,
        media_type="text/csv",
        filename=filename,
    )
