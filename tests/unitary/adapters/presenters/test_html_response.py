from http import HTTPStatus

from src.adapters.presenters.html_response import TemplateBuilder
from src.core.data.enums import Language
from tests.helpers.models import Request
from tests.mocks.common import CSRF_TOKEN


def test_search_template():
    request = Request()
    response = TemplateBuilder.search_template(
        request, CSRF_TOKEN, Language.EN_US
    )
    assert request.session.get("csrf-token") == CSRF_TOKEN
    assert response.status_code == HTTPStatus.OK
    assert response.media_type == "text/html" and response.body
    assert response.headers["Content-Language"] == Language.EN_US
    assert response.headers["X-CSRF-Token"] == CSRF_TOKEN


def test_not_found_template():
    response = TemplateBuilder.not_found_template(Request(), 404, "any")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.media_type == "text/html" and response.body
    assert response.headers["Content-Language"] == Language.EN_US
    assert response.headers["Location"].count("/v2/scopus-survey") == 1
    assert response.headers["Refresh"].count("5; /v2/scopus-survey") == 1
