from pandas import DataFrame
from thefuzz.fuzz import partial_ratio as fuzz_partial_ratio

from src.adapters.persistence.csv_builder import write_csv_file
from src.adapters.serializers.query_params import SurveyParams
from src.adapters.serializers.scopus_data import ScopusAbstract
from src.infra.config.config import FILE
from src.infra.config.scopus import DATA_SOURCE_NOTE
from tests.mocks.raw import (
    ALIAS_SEARCH_PARAMS,
    ALIAS_SEARCH_PARAMS_FULL,
    API_KEY,
    DIRECTORY,
    RAW_ABSTRACT_FULL,
    RAW_ABSTRACT_OK,
)


def test_write_csv_with_metadata():
    dataset = DataFrame([ScopusAbstract(**RAW_ABSTRACT_OK).model_dump()])
    params = SurveyParams(**ALIAS_SEARCH_PARAMS)
    filename = write_csv_file(dataset, params, ["any", "any"])
    file_path = DIRECTORY / f"{API_KEY}_{FILE}"

    assert filename == f"{API_KEY}_python-ai_{FILE}"
    assert file_path.exists()

    with file_path.open(mode="r") as file:
        lines = file.readlines()

    assert len(lines) == 6
    assert "# GeneratedBy: ScopusSurveyAPI" in lines[0]
    assert "# Params" in lines[1]
    assert API_KEY in lines[1]
    assert "Python AND AI" in lines[1]
    assert "# Survey" in lines[2]
    assert "any, any" in lines[2]
    assert "# Source" in lines[3]
    assert fuzz_partial_ratio(lines[3], DATA_SOURCE_NOTE) > 80
    assert "Article Preview Page URL" in lines[4]
    assert "Authors" in lines[4]
    assert "DOI" in lines[4]

    columns = lines[5].split(";")
    assert len(columns) == 11 and columns.count("") == 6


def test_write_csv_with_more_metadata():
    dataset = DataFrame([ScopusAbstract(**RAW_ABSTRACT_FULL).model_dump()])
    params = SurveyParams(**ALIAS_SEARCH_PARAMS_FULL)
    filename = write_csv_file(dataset, params, ["any", "any"])
    file_path = DIRECTORY / f"{API_KEY}_{FILE}"

    assert filename == f"{API_KEY}_python-ai_{FILE}"
    assert file_path.exists()

    with file_path.open(mode="r") as file:
        lines = file.readlines()

    assert len(lines) == 6
    assert "# GeneratedBy: ScopusSurveyAPI" in lines[0]
    assert "# Params" in lines[1]
    assert API_KEY in lines[1]
    assert "Python AND AI" in lines[1]
    assert "doctype=ar" in lines[1]
    assert "page_range=0-4" in lines[1]
    assert "# Survey" in lines[2]
    assert "any, any" in lines[2]
    assert "# Source" in lines[3]
    assert fuzz_partial_ratio(lines[3], DATA_SOURCE_NOTE) > 80
    assert "Article Preview Page URL" in lines[4]
    assert "Authors" in lines[4]
    assert "DOI" in lines[4]
    assert "any_title" in lines[5]
    assert "any_abstract" in lines[5]
    assert "any_author" in lines[5]
