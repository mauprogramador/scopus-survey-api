from json import loads

from pydantic_core import PydanticUndefined

from src.adapters.presenters.error_response import ErrorJSON, ErrorResponse
from src.core.common.error_messages import SERIALIZE_ERROR
from src.core.common.types import Json
from tests.mocks.helpers import fqn
from tests.mocks.raw import HTTP_500, REQUEST


def test_error_response():
    model = ErrorResponse(
        status_code=HTTP_500,
        status="any",
        message="any",
        request=REQUEST,
    )
    assert not model.success and model.timestamp
    assert model.status_code == HTTP_500
    assert model.status == "any" and model.message == "any"
    assert model.errors is None and model.request is not None
    assert model.request["url"] and model.request["host"]
    assert model.request["port"] and model.request["method"]
    assert model.request["headers"]


def test_error_json():
    model = ErrorJSON(
        REQUEST,
        HTTP_500,
        "any",
        [{"type": "any", "loc": "any"}],
    )
    raw: Json = loads(model.body.decode())  # type: ignore

    assert not raw["success"] and raw["timestamp"] is not None
    assert raw["status"] == HTTP_500.phrase
    assert raw["status_code"] == HTTP_500
    assert raw["message"] == "any"

    req, errors = raw["request"], raw["errors"]
    assert req is not None and errors is not None
    assert req["url"] and req["host"] and req["port"]
    assert req["method"] and req["headers"]
    assert errors[0]["type"] == "any" and errors[0]["loc"] == "any"


def test_error_json_dict_errors():
    model = ErrorJSON(
        REQUEST,
        HTTP_500,
        "any",
        {"type": "any"},
    )
    raw: Json = loads(model.body.decode())  # type: ignore

    assert not raw["success"] and raw["message"] == "any"
    assert raw["status_code"] == HTTP_500
    assert isinstance(raw["errors"], list) and raw["errors"][0]["type"]


def test_error_json_serialize_error():
    model = ErrorJSON(
        REQUEST,
        HTTP_500,
        "any",
        [{"type": PydanticUndefined}],
    )
    raw: Json = loads(model.body.decode())  # type: ignore

    assert not raw["success"] and raw["message"] == SERIALIZE_ERROR
    assert raw["status_code"] == HTTP_500
    assert raw["errors"][0]["type"] is None
    assert raw["errors"][1]["type"] == fqn(TypeError)
    assert raw["errors"][1]["detail"].endswith("not JSON serializable")
