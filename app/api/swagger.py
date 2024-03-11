from app.exceptions import HANDLERS, BaseExceptionResponse
from app.utils.lifespan import lifespan

TITLE = 'Scopus-Searcher-API'
VERSION = 'v1.0.0'
SUMMARY = 'API for Bibliographic Survey of Scopus Articles'
DESCRIPTION = """
[**Web Application**](http://127.0.0.1:8000/scopus-searcher/api)
&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
[**Documentation**](https://mauprogramador.github.io/scopus-searcher-api/)
"""

API_ROUTE_DESCRIPTION = """
**Keywords:** must be separated by a comma and each keyword can contain
letters, numbers, underscores and spaces, from 2 to 120 characters <br/><br/>
**Ex.:** Python, Machine Learning, Data Science, Neural Networks
"""
WEB_API_ROUTE_DESCRIPTION = """
**Web API:** <http://127.0.0.1:8000/scopus-searcher/api>
"""
WEB_TABLE_ROUTE_DESCRIPTION = """
**Web Table:** <http://127.0.0.1:8000/scopus-searcher/api/table>
"""


RESPONSES = {
    422: {
        'model': BaseExceptionResponse,
        'description': 'Base Exception Response',
    }
}
CONTACT = {
    'name': 'Mauricio',
    'email': 'mauricio.batista@estudante.ifms.edu.br',
}

FASTAPI = {
    'title': TITLE,
    'summary': SUMMARY,
    'description': DESCRIPTION,
    'version': VERSION,
    'docs_url': '/',
    'responses': RESPONSES,
    'contact': CONTACT,
    'exception_handlers': HANDLERS,
    'lifespan': lifespan,
}
