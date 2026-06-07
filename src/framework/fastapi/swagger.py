from http import HTTPStatus

from src import __contact__, __license__


APP_DESCRIPTION = """
<br>
[**`GET STARTED`**](/v2/scopus-survey/web/en-US/survey-bibliographies) **➡**
<br><br><br>
**Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso do Sul**
&nbsp;&#8226;&nbsp;
[IFMS Campus Três Lagoas](https://www.ifms.edu.br/campi/campus-tres-lagoas)
<br>
**Tecnologia em Análise e Desenvolvimento de Sistemas**
&nbsp;&#8226;&nbsp;
[TADS](https://www.ifms.edu.br/campi/campus-tres-lagoas/cursos/graduacao/\
analise-e-desenvolvimento-de-sistemas)

_Federal Institute of Education, Science and Technology of Mato Grosso do Sul_
<br>_Technology in Systems Analysis and Development_

**© 2024 [@mauprogramador](https://github.com/mauprogramador) and
[IFMS](https://www.ifms.edu.br). All rights reserved.**<br>
**Data provided by [Scopus](https://www.scopus.com)®
&nbsp;&#8226;&nbsp;
© [Elsevier](https://www.elsevier.com)**<br><br>

📦 [**Source Code**](https://github.com/mauprogramador/scopus-survey-api)
&nbsp;&#8226;&nbsp;
🌐 [**Web Application**](/v2/scopus-survey/web/en-US/survey-bibliographies)
&nbsp;&#8226;&nbsp;
📄 [**Documentation**](https://mauprogramador.github.io/scopus-survey-api/)
&nbsp;&#8226;&nbsp;
🔖 [**Latest Release**](https://github.com/mauprogramador/scopus-survey-api/\
releases/latest)

<br>
**References**
<br>
🔗 [API Key Settings](https://dev.elsevier.com/api_key_settings.html)
<br>
🔗 [Scopus Search API](https://dev.elsevier.com/documentation/\
ScopusSearchAPI.wadl)
<br>
🔗 [Abstract Retrieval API](https://dev.elsevier.com/documentation/\
AbstractRetrievalAPI.wadl)
<br>
🔗 [Scopus Academic Research](https://dev.elsevier.com/\
academic_research_scopus.html)
<br><br>
"""
TERMS_OF_SERVICE = (
    "https://github.com/mauprogramador/"
    "scopus-survey-api/blob/master/TERMS_OF_SERVICE.md"
)
CONTACT = {
    "name": "Maurício da Silva Batista (@mauprogramador)",
    "url": "https://github.com/mauprogramador",
    "email": __contact__,
}
LICENSE = {
    "name": "MIT License",
    "identifier": __license__,
    "url": "https://opensource.org/license/mit",
}
OPENAPI_EXTRA = {
    "security": [
        {
            "type": "apiKey",
            "in": "header",
            "name": "X-CSRF-Token",
        },
        {
            "type": "apiKey",
            "in": "cookie",
            "name": "csrf-token",
        },
    ]
}
ROUTE_DESCRIPTION = (
    "We implemented the Double-Submit Cookie method (stateless CSRF protection"
    " standard) with automatic client-side CSRF token validation for security."
)
JSON_ERROR_RESPONSE = {
    "description": "Error",
    "content": {
        "application/json": {
            "example": {
                "success": False,
                "status_code": 401,
                "status": "Unauthorized",
                "message": "CSRF token has expired",
                "timestamp": "2026-01-01T00:00:00Z",
                "request": {
                    "path": "/v2/scopus-survey/api/csv",
                    "method": "GET",
                },
                "tracking_id": "ERR_SignatureExpired_d51vk8e1Vd8c",
                "errors": [
                    {
                        "type": "itsdangerous.exc.SignatureExpired",
                        "message": "Signature age 3800 > 3600 seconds",
                    },
                ],
            }
        }
    },
}
HTML_SUCCESS_EXAMPLE = """
<!DOCTYPE html>
<html>
    <head>
        <title>Survey Bibliographies - ScopusSurveyAPI</title>
    </head>
    <body>...</body>
</html>
"""
HTML_ERROR_EXAMPLE = """
<!DOCTYPE html>
<html>
    <head>
        <title>Error - ScopusSurveyAPI</title>
    </head>
    <body>...</body>
</html>
"""
RESPONSES = {
    HTTPStatus.UNPROCESSABLE_ENTITY: JSON_ERROR_RESPONSE,
}
WEB_FORM_RESPONSES = {
    HTTPStatus.OK: {
        "description": "Success: Web Form Page",
        "content": {
            "text/html": {
                "example": HTML_SUCCESS_EXAMPLE,
            }
        },
    },
    HTTPStatus.BAD_REQUEST: {
        "description": "Error: Error Page",
        "content": {
            "text/html": {
                "example": HTML_ERROR_EXAMPLE,
            }
        },
    },
    HTTPStatus.UNPROCESSABLE_ENTITY: {
        "description": "Error: Error Page",
        "content": {
            "text/html": {
                "example": HTML_ERROR_EXAMPLE,
            }
        },
    },
}
JSON_RESPONSES = {
    HTTPStatus.OK: {
        "description": "Success: Totals of keyword combinations",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "status_code": 200,
                    "status": "OK",
                    "message": "Combination totals survey successfully",
                    "timestamp": "2026-01-01T00:00:00Z",
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
    HTTPStatus.BAD_REQUEST: JSON_ERROR_RESPONSE,
    HTTPStatus.UNPROCESSABLE_ENTITY: JSON_ERROR_RESPONSE,
}
CSV_RESPONSES = {
    HTTPStatus.OK: {
        "description": "Success: CSV file of bibliographies",
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
    HTTPStatus.BAD_REQUEST: JSON_ERROR_RESPONSE,
    HTTPStatus.UNPROCESSABLE_ENTITY: JSON_ERROR_RESPONSE,
}
