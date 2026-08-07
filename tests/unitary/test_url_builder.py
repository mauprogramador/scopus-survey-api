from urllib.parse import unquote_plus

from src.adapters.serializers.query_params import (
    CombinationParams,
    SurveyParams,
)
from src.adapters.types import (
    DocType,
    PageRange,
    PubStage,
    SrcType,
    SubjArea,
)
from src.infra.config.scopus import ARTICLE_PAGE_URL, SEARCH_FIELDS
from src.infra.http.url_builder import (
    build_abstract_urls,
    build_article_page_url,
    build_combination_urls,
    build_search_urls,
)
from tests.mocks.raw import (
    ALIAS_COMBINATION_PARAMS_FULL,
    ALIAS_SEARCH_PARAMS_FULL,
    API_KEY,
)


def test_build_article_page_url():
    url = build_article_page_url("any")
    assert ARTICLE_PAGE_URL in url
    assert "partnerID=HzOxMe3b" in url
    assert "scp=any" in url
    assert "origin=inward" in url


def test_build_combination_url():
    params = CombinationParams(**ALIAS_COMBINATION_PARAMS_FULL)
    builder = build_combination_urls(params)
    url = unquote_plus(builder("any"))

    assert "any" in url
    assert f"apiKey={API_KEY}" in url
    assert "query=TITLE-ABS-KEY(any)" in url
    assert f"DOCTYPE({DocType.AR})" in url
    assert f"PUBSTAGE({PubStage.FINAL})" in url
    assert "LANGUAGE(english)" in url
    assert "OPENACCESS(0)" in url
    assert f"SRCTYPE({SrcType.J})" in url
    assert f"SUBJAREA({SubjArea.COMP})" in url
    assert f"PAGES({PageRange.SHORT})" in url
    assert "field=dc:identifier" in url
    assert "suppressNavLinks=true" in url
    assert f"date={params.date}" in url
    assert "count=1" in url
    assert "sort=+pubyear,+coverDate,+relevancy" in url


def test_build_search_url():
    params = SurveyParams(**ALIAS_SEARCH_PARAMS_FULL)
    builder = build_search_urls(params)
    url = unquote_plus(builder(0))
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
    assert "field=dc:identifier" in url
    assert "suppressNavLinks=true" in url
    assert f"date={params.date}" in url
    assert "start=0" in url
    assert "sort=+pubyear,+coverDate,+relevancy" in url


def test_build_abstract_url():
    builder = build_abstract_urls(API_KEY)
    url = unquote_plus(builder("any_abstract_url"))
    search_fields = ",".join(SEARCH_FIELDS)

    assert "any_abstract_url" in url
    assert f"apiKey={API_KEY}" in url
    assert f"field={search_fields}" in url
