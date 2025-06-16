from math import ceil

from src.core.config.scopus import NULL
from src.core.data.enums import ScopusCode
from src.core.data.serializers import (
    ScopusAbstract,
    ScopusEntry,
    ScopusErrorResponse,
    ScopusQuotaRateLimit,
    ScopusSearch,
)


def test_scopus_entry():
    model = ScopusEntry.model_validate(
        {
            "@_fa": "true",
            "prism:url": "any",
            "dc:identifier": "SCOPUS_ID:any",
        }
    )
    assert model.link == "true"
    assert model.url == "any"
    assert model.scopus_id == "SCOPUS_ID:any"


def test_scopus_search():
    model = ScopusSearch.model_validate(
        {
            "search-results": {
                "opensearch:totalResults": 156,
                "opensearch:itemsPerPage": 25,
                "entry": [],
            }
        }
    )
    assert model.total_results == 156 and model.items_per_page == 25
    assert model.pages_count == ceil(156 / 25) and len(model.entry) == 0
    model.count_limit(100)
    assert model.total_results == 100 and model.pages_count == ceil(100 / 25)


def test_scopus_abstract():
    model = ScopusAbstract.model_validate(
        {
            "abstracts-retrieval-response": {
                "coredata": {
                    "dc:identifier": "SCOPUS_ID:123",
                    "eid": "any_eid",
                    "dc:title": "any_title",
                    "prism:publicationName": "any_publication_name",
                    "prism:volume": "any_volume",
                    "prism:coverDate": "any_date",
                    "prism:doi": "any_doi",
                    "citedby-count": "any_citations",
                    "dc:creator": {
                        "author": [{"ce:indexed-name": "any_author"}]
                    },
                }
            }
        }
    )
    assert model.scopus_id == "SCOPUS_ID:123" and model.eid == "any_eid"
    assert model.abstract == NULL and model.title == "any_title"
    assert model.publication_name == "any_publication_name"
    assert model.volume == "any_volume" and model.date == "any_date"
    assert model.doi == "any_doi" and model.citations == "any_citations"
    assert model.authors == "any_author" and model.url.count("123") == 1


def test_scopus_abstract_authors():
    model = ScopusAbstract.model_validate(
        {
            "abstracts-retrieval-response": {
                "coredata": {
                    "dc:identifier": "SCOPUS_ID:123",
                    "dc:title": "any_title",
                    "prism:publicationName": "any_publication_name",
                    "prism:coverDate": "any_date",
                    "dc:description": "any_description",
                },
                "authors": {
                    "author": [
                        {"ce:indexed-name": "any_author_1"},
                        {"ce:indexed-name": "any_author_2"},
                    ]
                },
            }
        }
    )
    assert model.abstract == "any_description"
    assert model.authors == "any_author_1, any_author_2"
    assert model.eid == NULL and model.volume == NULL
    assert model.doi == NULL and model.citations == NULL


def test_scopus_quota_rate_limit():
    model = ScopusQuotaRateLimit.model_validate(
        {
            "X-RateLimit-Limit": "20000",
            "X-RateLimit-Remaining": "20000",
            "X-RateLimit-Reset": "1746087344",
            "X-ELS-Status": "OK",
        }
    )
    assert model.limit == 20000 and model.remaining == 20000
    assert model.reset == 1746087344 and model.status == "OK"
    assert model.reset_datetime != NULL


def test_scopus_error_response():
    model = ScopusErrorResponse.model_validate(
        {"service-error": {"status": {"statusCode": ScopusCode.QUOTA}}}
    )
    assert model.code == ScopusCode.QUOTA

    model = ScopusErrorResponse.model_validate(
        {"error-response": {"error-code": ScopusCode.RATE_LIMIT}}
    )
    assert model.code == ScopusCode.RATE_LIMIT
