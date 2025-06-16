from tests.helpers.models import ScopusResponse

ONE_PAGE = ScopusResponse(
    {
        "search-results": {
            "opensearch:totalResults": 24,
            "opensearch:itemsPerPage": 25,
            "entry": [
                {
                    "@_fa": "true",
                    "prism:url": "https://api.elsevier.com/scopus_id/any",
                    "dc:identifier": "SCOPUS_ID:any",
                }
            ],
        }
    }
)
