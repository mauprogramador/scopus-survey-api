from pytest import fixture

from src.adapters.helpers.url_builder import URLBuilder
from tests.mocks.common import API_KEY, KEYWORDS, SEARCH_PARAMS
from tests.mocks.fixtures import URL_BUILDER


@fixture(scope="module", name="scopus_urls")
def scopus_apis_urls():
    yield URL_BUILDER


def test_search_url(scopus_urls: URLBuilder):
    url = scopus_urls.search_url(SEARCH_PARAMS)
    assert url.count(f"apiKey={API_KEY}") == 1
    assert url.count(KEYWORDS[0]) == 1
    assert url.count(f"date={SEARCH_PARAMS.year_range}") == 1


def test_pagination_url(scopus_urls: URLBuilder):
    url = scopus_urls.pagination_url(7)
    assert url.count("start=7") == 1


def test_abstract_url(scopus_urls: URLBuilder):
    scopus_urls.set_abstract_api_key(API_KEY)
    url = scopus_urls.abstract_url("any")
    assert url.count("any") == 1
    assert url.count(f"apiKey={API_KEY}") == 1
