from http import HTTPStatus
from json import loads

from pydantic_core import PydanticUndefined

from src.adapters.presenters.error_response import ErrorJSON, ErrorResponse
from src.core.common.messages import SERIALIZE_ERROR
from tests.helpers.models import Request


def test_error_response():
    response = ErrorResponse(
        status_code=500, status="any", message="any", request=Request()
    )
    assert not response.success and response.timestamp
    assert response.status_code == 500 and response.status == "any"
    assert response.message == "any" and response.errors is None
    assert response.request is not None


def test_error_json():
    response = ErrorJSON(
        Request("any"), 500, "any", [{"type": "any", "loc": "any"}]
    )
    response = loads(response.body.decode())

    assert not response["success"] and response["timestamp"] is not None
    assert response["status"] == HTTPStatus(500).phrase
    assert response["status_code"] == 500 and response["message"] == "any"
    assert response["request"] is not None
    assert response["errors"] is not None


def test_error_json_serialize_error():
    response = ErrorJSON(
        Request("any"), 500, "any", [{"type": PydanticUndefined}]
    )
    response = loads(response.body.decode())

    assert not response["success"] and response["timestamp"] is not None
    assert response["status"] == HTTPStatus(500).phrase
    assert response["status_code"] == 500
    assert response["message"] == SERIALIZE_ERROR
    assert response["request"] is not None
    assert response["errors"] == {"serialize_error": [{"type": None}]}
