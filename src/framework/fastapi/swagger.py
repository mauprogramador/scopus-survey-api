from http import HTTPStatus

from src.adapters.presenters.json_response import ErrorResponse

DESCRIPTION = """
🌐 [**Web Application**](/v2/scopus-survey/web/en-US/search-articles)
&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
📄 [**Documentation**](https://mauprogramador.github.io/scopus-survey-api/)

**Scopus Documentation:**
<br>🔑 [**API Key Settings**](https://dev.elsevier.com/api_key_settings.html)
<br>🔍 [**Scopus Search API**](https://dev.elsevier.com/documentation/\
ScopusSearchAPI.wadl)
<br>📄 [**Abstract Retrieval API**](https://dev.elsevier.com/documentation/\
AbstractRetrievalAPI.wadl)
"""
TERMS_OF_SERVICE = (
    "https://github.com/mauprogramador/"
    "scopus-survey-api/blob/master/TERMS_OF_SERVICE.md"
)
CONTACT = {
    "name": "@mauprogramador",
    "url": "https://github.com/mauprogramador",
    "email": "sir.silvabmauricio@gmail.com",
}
LICENSE = {
    "name": "MIT License",
    "identifier": "MIT",
    "url": (
        "https://github.com/mauprogramador/"
        "scopus-survey-api/blob/master/LICENSE"
    ),
}
RESPONSES = {
    HTTPStatus.BAD_REQUEST: {
        "model": ErrorResponse,
        "description": "JSON error response",
    },
    HTTPStatus.UNPROCESSABLE_ENTITY: {
        "model": ErrorResponse,
        "description": "JSON error response",
    },
}

HTML_RESPONSE = {
    200: {
        "description": "Web Page",
        "content": {
            "text/html": {
                "example": "<html>...</html>",
            }
        },
    }
}
JSON_RESPONSE = {
    200: {
        "description": "JSON response",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "status_code": 200,
                    "status": "OK",
                    "message": "Combination totals survey successfully",
                    "timestamp": "2025-01-01T00:00:00Z",
                    "data": [
                        {
                            "combination": "Python AND Georeference",
                            "total": 2,
                        },
                        {
                            "combination": "Python AND Web OR API",
                            "total": 3391,
                        },
                    ],
                },
            }
        },
    },
}
CSV_RESPONSE = {
    200: {
        "description": "CSV file of the articles found",
        "content": {
            "text/csv": {
                "example": (
                    "Article Preview Page URL;Scopus ID;Authors;Title;"
                    "Publication Name;Abstract;Date;Electronic ID;DOI;"
                    "Volume;Citations\nhttps://www.scopus.com/inward/"
                    "record.uri?partnerID=HzOxMe3b&scp=85183327527&origin"
                    "=inward;SCOPUS_ID:85183327527;Roman A.;Enhancing "
                    "Georeferencing and Mosaicking Techniques over Water "
                    "Surfaces with High-Resolution Unmanned Aerial Vehicle "
                    "(UAV) Imagery;Remote Sensing;null;2024-01-01;2-s2.0-85"
                    "183327527;10.3390/rs16020290;16;11"
                ),
            }
        },
    },
}
