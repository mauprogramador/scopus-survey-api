from unittest import TestCase

from pydantic_core import ValidationError
from pytest import raises

from src.core.config.scopus import CURRENT_YEAR, LAST_DECADE, LAST_THREE_YEARS
from src.core.data.query_params import CSVParams, SearchParams
from tests.mocks.common import API_KEY, CSRF_TOKEN, KEYWORDS


class CSVParamsTest(TestCase):

    def api_key(self, api_key: str) -> CSVParams:
        return CSVParams(**{"api_key": api_key, "csrf_token": CSRF_TOKEN})

    def test_model(self):
        model = CSVParams(**{"api_key": API_KEY, "csrf_token": CSRF_TOKEN})
        assert model.api_key == API_KEY and model.csrf_token == CSRF_TOKEN

        with raises(ValidationError) as exc:
            CSVParams(**{"api_key": API_KEY, "any": "any"})
        assert exc.value.errors()[0]["type"] == "extra_forbidden"

    def test_validation_api_key(self):
        with raises(ValidationError) as exc:
            CSVParams(**{"csrf_token": CSRF_TOKEN})
        assert exc.value.errors()[0]["type"] == "missing"

        with raises(ValidationError) as exc:
            self.api_key("any")
        assert exc.value.errors()[0]["type"] == "string_too_short"

        with raises(ValidationError) as exc:
            self.api_key("x" * 40)
        assert exc.value.errors()[0]["type"] == "string_too_long"

        with raises(ValidationError) as exc:
            self.api_key("b@5$" * 8)
        assert exc.value.errors()[0]["type"] == "string_pattern_mismatch"

    def test_validation_csrf_token(self):
        model = CSVParams(**{"api_key": API_KEY})
        assert model.csrf_token is None

        model = CSVParams(**{"api_key": API_KEY, "csrf_token": "any"})
        assert model.csrf_token == "any"


class SearchParamsTest(TestCase):

    def search(self, **kwargs) -> SearchParams:
        data = {
            "api_key": API_KEY,
            "csrf_token": CSRF_TOKEN,
            "keywords": KEYWORDS,
        }
        data.update(kwargs)
        return SearchParams(**data)

    def test_model(self):
        params = self.search(
            max_count=25,
            ratio=0,
            start_year=2020,
            end_year=2022,
        )
        assert params.api_key == API_KEY and params.csrf_token == CSRF_TOKEN
        assert params.keywords == KEYWORDS and params.year_range
        assert params.ratio == 0 and params.max_count == 25
        assert params.start_year == 2020 and params.end_year == 2022

    def test_missing_others_params(self):
        params = self.search()
        assert params.max_count == 25 and params.ratio == 80
        assert params.start_year == LAST_THREE_YEARS
        assert params.end_year == CURRENT_YEAR

    def test_extra_forbidden(self):
        with raises(ValidationError) as exc:
            self.search(any="any")
        assert exc.value.errors()[0]["type"] == "extra_forbidden"

    def test_max_count_validation(self):
        with raises(ValidationError) as exc:
            self.search(max_count=275)
        assert exc.value.errors()[0]["type"] == "less_than_equal"

        with raises(ValidationError) as exc:
            self.search(max_count=201)
        assert exc.value.errors()[0]["type"] == "multiple_of"

    def test_ratio_validation(self):
        with raises(ValidationError) as exc:
            self.search(ratio=-1)
        assert exc.value.errors()[0]["type"] == "greater_than_equal"

        with raises(ValidationError) as exc:
            self.search(ratio=101)
        assert exc.value.errors()[0]["type"] == "less_than_equal"

    def test_start_year_validation(self):
        with raises(ValidationError) as exc:
            self.search(start_year=LAST_DECADE - 1)
        assert exc.value.errors()[0]["type"] == "greater_than_equal"

        with raises(ValidationError) as exc:
            self.search(start_year=CURRENT_YEAR)
        assert exc.value.errors()[0]["type"] == "less_than_equal"

    def test_end_year_validation(self):
        with raises(ValidationError) as exc:
            self.search(end_year=LAST_DECADE)
        assert exc.value.errors()[0]["type"] == "greater_than_equal"

        with raises(ValidationError) as exc:
            self.search(end_year=CURRENT_YEAR + 1)
        assert exc.value.errors()[0]["type"] == "less_than_equal"


class SearchParamsKeywordsTest(TestCase):

    def keywords(self, keywords: list[str]) -> SearchParams:
        return SearchParams(
            **{
                "api_key": API_KEY,
                "csrf_token": CSRF_TOKEN,
                "keywords": keywords,
            }
        )

    def test_missing(self):
        with raises(ValidationError) as exc:
            SearchParams(**{"api_key": API_KEY, "csrf_token": CSRF_TOKEN})
        assert exc.value.errors()[0]["type"] == "missing"

    def test_one_line(self):
        params = self.keywords(["any,any"])
        assert params.keywords == ["any", "any"]

    def test_keyword_length(self):
        with raises(ValidationError) as exc:
            self.keywords(["x"])
        assert exc.value.errors()[0]["type"] == "string_too_short"

        with raises(ValidationError) as exc:
            self.keywords(["any" * 50])
        assert exc.value.errors()[0]["type"] == "string_too_long"

    def test_keywords_list_length(self):
        with raises(ValidationError) as exc:
            self.keywords(["any"] * 5)
        assert exc.value.errors()[0]["type"] == "too_long"

        with raises(ValidationError) as exc:
            self.keywords(["any,any,any,any,any"])
        assert exc.value.errors()[0]["type"] == "too_long"

    def test_keyword_mismatch(self):
        with raises(ValidationError) as exc:
            self.keywords(["any", "e#v%"])
        assert exc.value.errors()[0]["type"] == "string_pattern_mismatch"
