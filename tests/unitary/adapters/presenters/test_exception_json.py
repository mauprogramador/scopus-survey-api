from app.adapters.presenters.exception_json import ExceptionJSON
from tests.helpers.utils import exception_response
from tests.mocks.unitary import EMPTY_REQUEST, ERRORS, ERRORS_UNDEFINED


def test_success():
    response = ExceptionJSON(EMPTY_REQUEST, 500, "any")
    exc_response = exception_response(response)

    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == "any"
    assert exc_response.request
    assert exc_response.errors is None
    assert exc_response.timestamp is not None


def test_errors():
    response = ExceptionJSON(EMPTY_REQUEST, 500, "any", ERRORS)
    exc_response = exception_response(response)

    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == "any"
    assert exc_response.errors is not None
    assert exc_response.errors[0]["type"] == "any"
    assert exc_response.errors[0]["loc"] == "any"
    assert exc_response.timestamp is not None


def test_filter():
    response = ExceptionJSON(EMPTY_REQUEST, 500, "any", ERRORS_UNDEFINED)
    exc_response = exception_response(response)

    assert not exc_response.success
    assert exc_response.code == 500
    assert exc_response.message == "any"
    assert exc_response.errors is not None
    assert exc_response.errors[0]["input"] is None
    assert exc_response.timestamp is not None
