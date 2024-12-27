from http import HTTPStatus
from os.path import join

from fastapi.responses import FileResponse
from pandas import DataFrame

from app.core.config.config import DIRECTORY, FILE
from app.core.domain.metaclasses import CSVResponseABC
from app.core.data.serializers import CSVFileHeaders


class CSVResponse(CSVResponseABC):
    """Generates CSV file responses"""

    __MEDIA_TYPE = "text/csv"
    __SEP = ";"

    @classmethod
    def build(cls, api_key: str, dataframe: DataFrame = None) -> FileResponse:
        filename = f"{api_key}_{FILE}"
        file_path = join(DIRECTORY, filename)

        if dataframe is not None:
            dataframe.to_csv(file_path, sep=cls.__SEP, index=False)

        headers = CSVFileHeaders.build(filename, api_key)

        return FileResponse(
            path=file_path,
            status_code=HTTPStatus.OK,
            headers=headers,
            media_type=cls.__MEDIA_TYPE,
            filename=filename,
        )
