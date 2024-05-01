from io import StringIO
from json import loads

from fastapi.responses import FileResponse, JSONResponse
from httpx import Response
from pandas import DataFrame, read_csv

from tests.data.models import FakeResponse


def get_csv_file(tmpdir) -> FileResponse:
    with open(f'{tmpdir}/articles.csv', 'w', encoding='utf-8') as file:
        file.write('Any')
    return FileResponse(f'{tmpdir}/articles.csv')


def load_body(response: JSONResponse) -> dict:
    return loads(response.body.decode('utf-8'))


def get_api_response(
    total_results: str, entry: list[dict[str, str]] = None
) -> FakeResponse:
    return FakeResponse(
        {
            'search-results': {
                'opensearch:totalResults': total_results,
                'opensearch:itemsPerPage': '25',
                'entry': entry,
            }
        }
    )


def assert_csv_response(response: Response) -> None:
    dataframe = read_csv(StringIO(response.text), sep=';')
    assert response.status_code == 200
    assert dataframe['Authors'].values.take(0) == 'Any Author'
    assert dataframe['Abstract'].values.take(0) == 'Any Abstract'


def load_groups(context: dict[str, int] | list[str]) -> DataFrame:
    groups: list[dict[str, str]] = []
    if isinstance(context, list):
        groups.extend(
            {'Authors': f'any_author{index}', 'Title': item}
            for index, item in enumerate(context)
        )
    else:
        for key, value in context.items():
            for count in range(value):
                title = key if value == 1 else f'{key}{value}-{count+1}'
                group = {'Authors': f'any_author{value}', 'Title': title}
                groups.append(group)
    return DataFrame(groups)
