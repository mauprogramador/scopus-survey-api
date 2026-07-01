from pydantic_core import ValidationError
from pytest import raises

from src.core.config.scopus import CURRENT_YEAR, LAST_THREE_YEARS
from src.core.data.enums import (
    Button,
    DocType,
    PageRange,
    PubStage,
    SrcType,
    SubjArea,
)
from src.core.data.query_params import (
    CombinationParams,
    CSVParams,
    SurveyParams,
)
from tests.mocks.raw import (
    ALIAS_COMBINATION_PARAMS,
    ALIAS_COMBINATION_PARAMS_FULL,
    ALIAS_CSV_PARAMS,
    ALIAS_SEARCH_PARAMS,
    ALIAS_SEARCH_PARAMS_FULL,
    API_KEY,
    KEYWORDS,
)


def test_csv_params_valid_data():
    model = CSVParams(**ALIAS_CSV_PARAMS)
    assert model.api_key == API_KEY and model.button == Button.PREVIOUS


def test_csv_params_raise_errors():
    with raises(ValidationError) as info:
        CSVParams(**{})
    assert len(info.value.errors()) == 2


def test_combination_params_valid_data():
    model = CombinationParams(**ALIAS_COMBINATION_PARAMS)
    assert model.api_key == API_KEY and model.keywords == KEYWORDS
    assert model.start_year == LAST_THREE_YEARS
    assert model.end_year == CURRENT_YEAR
    assert not model.doctype and not model.pubstage
    assert not model.language and not model.open_access
    assert not model.source_type and not model.subject_area
    assert not model.page_range and model.button == Button.COMBINATION
    assert model.date == f"{model.start_year}-{model.end_year}"


def test_combination_params_overridden_default():
    model = CombinationParams(**ALIAS_COMBINATION_PARAMS_FULL)
    assert model.api_key == API_KEY and model.keywords == KEYWORDS
    assert model.start_year == 2020 and model.end_year == 2021
    assert model.doctype == DocType.AR
    assert model.pubstage == PubStage.FINAL
    assert model.language == "english" and model.open_access == "0"
    assert model.source_type == SrcType.J
    assert model.subject_area == SubjArea.COMP
    assert model.page_range == PageRange.SHORT
    assert model.button == Button.COMBINATION
    assert model.date == f"{model.start_year}-{model.end_year}"


def test_combination_params_raise_errors():
    with raises(ValidationError) as info:
        CombinationParams(**{})
    assert len(info.value.errors()) == 3


def test_combination_params_empty_to_default():
    raw = {
        "api_key": API_KEY,
        "doctype": "",
        "pubstage": " ",
        "keywords": KEYWORDS,
        "button": Button.COMBINATION.value,
    }
    model = CombinationParams(**raw)
    assert not model.doctype and not model.pubstage


def test_combination_params_keywords():
    raw = {
        "api_key": API_KEY,
        "keywords": ["any,any"],
        "button": Button.COMBINATION.value,
    }
    model = CombinationParams(**raw)
    assert model.keywords == ["any", "any"]

    raw.update({"keywords": ["any,any,any,any,any"]})
    with raises(ValidationError) as info:
        CombinationParams(**raw)
    assert info.value.errors()[0]["type"] == "too_long"

    raw.update({"keywords": ["any", "any", "any", "any", "any"]})
    with raises(ValidationError) as info:
        CombinationParams(**raw)
    assert info.value.errors()[0]["type"] == "too_long"

    raw.update({"keywords": ["any"]})
    with raises(ValidationError) as info:
        CombinationParams(**raw)
    assert info.value.errors()[0]["type"] == "too_short"


def test_search_params_valid_data():
    model = SurveyParams(**ALIAS_SEARCH_PARAMS)
    assert model.api_key == API_KEY and model.keywords == KEYWORDS
    assert model.combination == "Python AND AI"
    assert model.button == Button.SURVEY
    assert model.ratio == 80
    assert model.date == f"{model.start_year}-{model.end_year}"


def test_search_params_overridden_default():
    model = SurveyParams(**ALIAS_SEARCH_PARAMS_FULL)
    assert model.api_key == API_KEY and model.keywords == KEYWORDS
    assert model.combination == "Python AND AI"
    assert model.button == Button.SURVEY
    assert model.ratio == 25


def test_search_params_raise_errors():
    with raises(ValidationError) as info:
        SurveyParams(**{})
    assert len(info.value.errors()) == 4


def test_search_params_empty_to_default():
    raw = {
        "api_key": API_KEY,
        "doctype": "",
        "pubstage": " ",
        "keywords": KEYWORDS,
        "combination": "Python",
        "button": Button.SURVEY.value,
    }
    model = SurveyParams(**raw)
    assert not model.doctype and not model.pubstage
