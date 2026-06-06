import json

from pydantic_core import PydanticUndefined, to_jsonable_python
from pytest_mock import MockerFixture as Mocker

from src.adapters.presenters.json_response import (
    ErrorJSON,
    ErrorResponse,
    SuccessJSON,
    SuccessResponse,
)
from src.core.common.types import Json
from src.core.data.enums import ExcMsg
from tests.mocks.helpers import fqn
from tests.mocks.raw import HTTP_200, HTTP_500, REQUEST


JSONABLE = fqn(ErrorJSON, to_jsonable_python)


def test_error_response():
    model = ErrorResponse(
        success=False,
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
    raw: Json = json.loads(model.body.decode())  # type: ignore

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
    raw: Json = json.loads(model.body.decode())  # type: ignore

    assert not raw["success"] and raw["message"] == "any"
    assert raw["status_code"] == HTTP_500
    assert isinstance(raw["errors"], list) and raw["errors"][0]["type"]


def test_error_json_serialize_fallback():
    model = ErrorJSON(
        REQUEST,
        HTTP_500,
        "any",
        [{"type": PydanticUndefined}, {"exc": RuntimeError}],
    )
    raw: Json = json.loads(model.body.decode())  # type: ignore

    assert not raw["success"] and raw["message"] == "any"
    assert raw["status_code"] == HTTP_500
    assert raw["errors"][0]["type"] == repr(PydanticUndefined)
    assert raw["errors"][1]["exc"] == repr(RuntimeError)


def test_error_json_serialize_error(mocker: Mocker):
    mocker.patch(JSONABLE, side_effect=ValueError("any"))
    model = ErrorJSON(REQUEST, HTTP_500, "any", [{"any": "any"}])
    raw: Json = json.loads(model.body.decode())  # type: ignore

    assert not raw["success"] and raw["message"] == "any"
    assert raw["status_code"] == HTTP_500
    assert raw["errors"][0]["type"] == fqn(ValueError)
    assert raw["errors"][0]["message"] == "any"
    assert raw["errors"][1]["desc"] == ExcMsg.SERIALIZE_ERROR
    assert raw["errors"][1]["raw_repr"]


def test_success_response():
    model = SuccessResponse(
        success=True,
        status_code=HTTP_200,
        status="any",
        message="any",
        data={"any": "any"},
    )
    assert model.success and model.timestamp
    assert model.status_code == HTTP_200
    assert model.status == "any" and model.message == "any"
    assert model.data is not None


def test_success_json():
    model = SuccessJSON(
        {"any": "any"},
        "any",
        {"any": "any"},
    )
    raw: Json = json.loads(model.body.decode())  # type: ignore

    assert raw["success"] and raw["timestamp"] is not None
    assert raw["status"] == HTTP_200.phrase
    assert raw["status_code"] == HTTP_200
    assert raw["message"] == "any" and raw["data"] is not None
