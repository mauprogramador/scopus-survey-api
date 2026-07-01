from pandas import DataFrame
from thefuzz.fuzz import partial_ratio as fuzz_partial_ratio

from src.core.config.config import DIRECTORY, FILE
from src.core.config.scopus import DATA_SOURCE_NOTE
from src.core.data.csv_builder import write_csv_file
from src.core.data.query_params import SurveyParams
from tests.mocks.raw import (
    ALIAS_SEARCH_PARAMS,
    ALIAS_SEARCH_PARAMS_FULL,
    API_KEY,
)


def test_write_csv_with_metadata():
    docs = DataFrame({"Title": ["any_title_1", "any_title_2"]})
    params = SurveyParams(**ALIAS_SEARCH_PARAMS)

    filename = write_csv_file(docs, params, ["any", "any"])
    file_path = DIRECTORY / f"{API_KEY}_{FILE}"

    assert filename == f"{API_KEY}_python-ai_{FILE}"
    assert file_path.exists()

    with file_path.open(mode="r") as file:
        lines = file.readlines()
        assert len(lines) == 7

        assert lines[0].startswith("# GeneratedBy")
        assert lines[1].startswith("# Params")
        assert lines[2].startswith("# Survey")
        assert lines[3].startswith("# Source")

        assert lines[1].count(API_KEY) == 1
        assert lines[1].count("Python AND AI") == 1
        assert lines[2].count("any") == 2
        assert fuzz_partial_ratio(lines[3], DATA_SOURCE_NOTE) > 80


def test_csv_with_more_metadata():
    docs = DataFrame({"Title": ["any_title_1", "any_title_2"]})
    params = SurveyParams(**ALIAS_SEARCH_PARAMS_FULL)

    filename = write_csv_file(docs, params, ["any", "any"])
    file_path = DIRECTORY / f"{API_KEY}_{FILE}"

    assert filename == f"{API_KEY}_python-ai_{FILE}"
    assert file_path.exists()

    with file_path.open(mode="r") as file:
        lines = file.readlines()
        assert len(lines) == 7

        assert lines[0].startswith("# GeneratedBy")
        assert lines[1].startswith("# Params")
        assert lines[2].startswith("# Survey")
        assert lines[3].startswith("# Source")

        assert lines[1].count(API_KEY) == 1
        assert lines[1].count("Python AND AI") == 1
        assert lines[1].count("doctype=ar") == 1
        assert lines[1].count("page_range=0-4") == 1
        assert lines[2].count("any") == 2
        assert fuzz_partial_ratio(lines[3], DATA_SOURCE_NOTE) > 80
