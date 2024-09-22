from tests.mocks.fixtures import URL_BUILDER


def test_search_url():
    url = URL_BUILDER.get_search_url(["any", "any"])
    assert url and url.count("any") == 2


def test_pagination_url():
    url = URL_BUILDER.get_search_url(["any", "any"])
    assert url and url.count("any") == 2
    url = URL_BUILDER.get_pagination_url(7)
    assert url.count("7") == 1


def test_abstract_url():
    url = URL_BUILDER.get_abstract_url("any")
    assert url and url.count("any") == 1
