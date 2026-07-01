from urllib.parse import unquote_plus

from src.adapters.helpers.url_builder import URLBuilder
from src.core.config.scopus import ARTICLE_PAGE_URL, SEARCH_FIELDS
from src.core.data.enums import DocType, PageRange, PubStage, SrcType, SubjArea
from src.core.data.query_params import CombinationParams, SurveyParams
from tests.mocks.raw import (
    ALIAS_COMBINATION_PARAMS,
    ALIAS_COMBINATION_PARAMS_FULL,
    ALIAS_SEARCH_PARAMS,
    ALIAS_SEARCH_PARAMS_FULL,
    API_KEY,
)


URL_BUILDER = URLBuilder()


def test_article_page_url():
    url = URL_BUILDER.article_page_url("any")
    assert ARTICLE_PAGE_URL in url
    assert "partnerID=HzOxMe3b" in url
    assert "scp=any" in url
    assert "origin=inward" in url


def test_combination_url():
    params = CombinationParams(**ALIAS_COMBINATION_PARAMS)
    URL_BUILDER.set_combination_query(params)
    bundle = URL_BUILDER.combination_url(("any",))
    url = unquote_plus(bundle.url)

    assert bundle.combination == "any"
    assert f"apiKey={API_KEY}" in url
    assert "query=TITLE-ABS-KEY(any)" in url
    assert "field=dc:identifier" in url
    assert "suppressNavLinks=true" in url
    assert f"date={params.date}" in url
    assert "count=1" in url
    assert "sort=+pubyear,+coverDate,+relevancy" in url


def test_combination_url_full():
    params = CombinationParams(**ALIAS_COMBINATION_PARAMS_FULL)
    URL_BUILDER.set_combination_query(params)
    bundle = URL_BUILDER.combination_url(("any",))
    url = unquote_plus(bundle.url)

    assert bundle.combination == "any"
    assert f"apiKey={API_KEY}" in url
    assert "query=TITLE-ABS-KEY(any)" in url
    assert f"DOCTYPE({DocType.AR})" in url
    assert f"PUBSTAGE({PubStage.FINAL})" in url
    assert "LANGUAGE(english)" in url
    assert "OPENACCESS(0)" in url
    assert f"SRCTYPE({SrcType.J})" in url
    assert f"SUBJAREA({SubjArea.COMP})" in url
    assert f"PAGES({PageRange.SHORT})" in url


def test_search_url():
    params = SurveyParams(**ALIAS_SEARCH_PARAMS)
    url = URL_BUILDER.search_url(params)
    url = unquote_plus(url)
    query = params.combination

    assert f"apiKey={API_KEY}" in url
    assert f"query=TITLE-ABS-KEY({query})" in url
    assert "field=dc:identifier" in url
    assert "suppressNavLinks=true" in url
    assert f"date={params.date}" in url
    assert "start=0" in url
    assert "sort=+pubyear,+coverDate,+relevancy" in url


def test_search_url_full():
    params = SurveyParams(**ALIAS_SEARCH_PARAMS_FULL)
    url = URL_BUILDER.search_url(params)
    url = unquote_plus(url)
    query = params.combination

    assert f"apiKey={API_KEY}" in url
    assert f"query=TITLE-ABS-KEY({query})" in url
    assert f"DOCTYPE({DocType.AR})" in url
    assert f"PUBSTAGE({PubStage.FINAL})" in url
    assert "LANGUAGE(english)" in url
    assert "OPENACCESS(0)" in url
    assert f"SRCTYPE({SrcType.J})" in url
    assert f"SUBJAREA({SubjArea.COMP})" in url
    assert f"PAGES({PageRange.SHORT})" in url


def test_pagination_url():
    params = SurveyParams(**ALIAS_SEARCH_PARAMS)
    URL_BUILDER.search_url(params)
    url = URL_BUILDER.pagination_url(page=7)

    url = unquote_plus(url)
    query = params.combination

    assert f"apiKey={API_KEY}" in url
    assert f"query=TITLE-ABS-KEY({query})" in url
    assert "start=7" in url


def test_abstract_url():
    URL_BUILDER.set_abstract_query(API_KEY)
    url = URL_BUILDER.abstract_url("any_abstract_url")

    url = unquote_plus(url)
    search_fields = ",".join(SEARCH_FIELDS)

    assert "any_abstract_url" in url
    assert f"apiKey={API_KEY}" in url
    assert f"field={search_fields}" in url
