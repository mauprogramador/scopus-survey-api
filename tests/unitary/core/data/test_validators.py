from pydantic_core import ValidationError
from pytest import raises

from app.core.common.messages import INVALID_KEYWORD
from app.core.common.types import SearchParams, Token
from app.core.config.config import TOKEN
from tests.mocks import common as data
from tests.mocks import fixtures as fix


def test_valid_search_params():
    search_params = SearchParams(api_key=data.API_KEY, keywords=data.KEYWORDS)
    assert search_params.api_key == data.API_KEY
    assert search_params.keywords == data.KEYWORDS


def test_missing_api_key():
    with raises(ValidationError) as error:
        SearchParams(keywords=data.KEYWORDS)
    assert error.value.errors()[0]["msg"] == fix.FIELD_REQUIRED


def test_invalid_short_api_key():
    with raises(ValidationError) as error:
        SearchParams(api_key="any", keywords=data.KEYWORDS)
    assert error.value.errors()[0]["msg"] == fix.INVALID_SHORT_VALUE


def test_invalid_long_api_key():
    with raises(ValidationError) as error:
        SearchParams(api_key=data.INVALID_LONG_VALUE, keywords=data.KEYWORDS)
    assert error.value.errors()[0]["msg"] == fix.INVALID_LONG_VALUE


def test_invalid_pattern_api_key():
    with raises(ValidationError) as error:
        api_key = data.INVALID_PATTERN_VALUE
        SearchParams(api_key=api_key, keywords=data.KEYWORDS)
    assert error.value.errors()[0]["msg"] == fix.INVALID_PATTERN


def test_missing_keywords():
    with raises(ValidationError) as error:
        SearchParams(api_key=data.API_KEY)
    assert error.value.errors()[0]["msg"] == fix.FIELD_REQUIRED


def test_invalid_short_keywords():
    with raises(ValidationError) as error:
        SearchParams(api_key=data.API_KEY, keywords=["any"])
    assert error.value.errors()[0]["msg"] == fix.MIN_SIZE_LIST


def test_invalid_long_keywords():
    with raises(ValidationError) as error:
        SearchParams(api_key=data.API_KEY, keywords=["any"] * 5)
    assert error.value.errors()[0]["msg"] == fix.MAX_SIZE_LIST


def test_invalid_pattern_keywords():
    with raises(ValidationError) as error:
        keywords = ["any", data.INVALID_PATTERN_VALUE]
        SearchParams(api_key=data.API_KEY, keywords=keywords)
    assert error.value.errors()[0]["msg"].count(INVALID_KEYWORD)


def test_invalid_blank_keyword():
    with raises(ValidationError) as error:
        SearchParams(api_key=data.API_KEY, keywords=["any", "  "])
    assert error.value.errors()[0]["msg"].count(INVALID_KEYWORD)


def test_invalid_data():
    with raises(ValidationError) as error:
        SearchParams(api_key="any", keywords=["  "])
    assert error.value.error_count() == 2


def test_valid_token():
    token = Token.validate_strings(TOKEN)
    assert token == TOKEN


def test_invalid_short_token():
    with raises(ValidationError) as error:
        Token.validate_strings("any")
    assert error.value.errors()[0]["msg"] == fix.INVALID_SHORT_VALUE


def test_invalid_long_token():
    with raises(ValidationError) as error:
        Token.validate_strings(data.INVALID_LONG_VALUE)
    assert error.value.errors()[0]["msg"] == fix.INVALID_LONG_VALUE


def test_invalid_pattern_token():
    with raises(ValidationError) as error:
        Token.validate_strings(data.INVALID_PATTERN_VALUE)
    assert error.value.errors()[0]["msg"] == fix.INVALID_PATTERN
