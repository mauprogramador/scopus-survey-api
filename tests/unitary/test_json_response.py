import json

from pydantic_core import PydanticUndefined, to_jsonable_python
from pytest_mock import MockerFixture as Mocker

from src.adapters.presenters.json_response import (
    ErrorJSON,
    ErrorResponse,
    SuccessJSON,
    SuccessResponse,
    json_response,
)
from src.adapters.serializers.query_params import CombinationParams
from src.adapters.serializers.scopus_data import ScopusHeaders
from src.core.domain.types import ExcMsg, Json
from tests.mocks.helpers import fqn
from tests.mocks.raw import (
    ALIAS_COMBINATION_PARAMS,
    API_KEY,
    HTTP_200,
    HTTP_400,
    HTTP_500,
    RAW_HEADERS_OK,
    REQUEST,
)


JSONABLE = fqn(ErrorJSON, to_jsonable_python)


def test_error_response():
    model = ErrorResponse(
        success=False,
        status_code=HTTP_500,
        status="any",
        message="any",
        tracking_id="any",
        request={"any": "any"},
    )
    assert not model.success and model.timestamp
    assert model.status_code == HTTP_500
    assert model.status == "any" and model.message == "any"
    assert model.details is None and model.request is not None
    assert model.request["any"] == "any"


def test_error_json():
    model = ErrorJSON(
        REQUEST,
        HTTP_500,
        "any",
        "any",
        [{"type": "any", "loc": "any"}],
    )
    raw: Json = json.loads(model.body.decode())  # type: ignore

    assert not raw["success"] and raw["timestamp"] is not None
    assert raw["status"] == HTTP_500.phrase
    assert raw["status_code"] == HTTP_500
    assert raw["message"] == "any"

    req, details = raw["request"], raw["details"]
    assert req is not None and details is not None
    assert req["path"] and req["method"]
    assert details[0]["type"] == "any" and details[0]["loc"] == "any"


def test_error_json_dict_errors():
    model = ErrorJSON(
        REQUEST,
        HTTP_500,
        "any",
        "any",
        {"type": "any"},
    )
    raw: Json = json.loads(model.body.decode())  # type: ignore

    assert not raw["success"] and raw["message"] == "any"
    assert raw["status_code"] == HTTP_500
    assert isinstance(raw["details"], list) and raw["details"][0]["type"]


def test_error_json_serialize_fallback():
    model = ErrorJSON(
        REQUEST,
        HTTP_500,
        "any",
        "any",
        [{"type": PydanticUndefined}, {"exc": RuntimeError}],
    )
    raw: Json = json.loads(model.body.decode())  # type: ignore

    assert not raw["success"] and raw["message"] == "any"
    assert raw["status_code"] == HTTP_500
    assert raw["details"][0]["type"] == repr(PydanticUndefined)
    assert raw["details"][1]["exc"] == repr(RuntimeError)


def test_error_json_serialize_error(mocker: Mocker):
    mocker.patch(JSONABLE, side_effect=ValueError("any"))
    message, details = "Ops!", [{"any": "any"}]
    model = ErrorJSON(REQUEST, HTTP_400, message, "any", details)
    raw: Json = json.loads(model.body.decode())  # type: ignore

    assert not raw["success"] and raw["message"] == ExcMsg.SERIALIZE_ERROR
    assert raw["status_code"] == HTTP_500
    assert raw["details"][0]["type"] == fqn(ValueError)
    assert raw["details"][0]["message"] == "any"
    assert raw["details"][0]["original_error"]["message"] == message
    assert raw["details"][0]["original_error"]["status_code"] == HTTP_400
    assert raw["details"][0]["original_error"]["raw_details"] == repr(details)


def test_success_response():
    model = SuccessResponse(
        success=True,
        status_code=HTTP_200,
        status="any",
        message="any",
        result={"any": "any"},
    )
    assert model.success and model.timestamp
    assert model.status_code == HTTP_200
    assert model.status == "any" and model.message == "any"
    assert model.result is not None


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
    assert raw["message"] == "any" and raw["result"] is not None


def test_json_response():
    params = CombinationParams(**ALIAS_COMBINATION_PARAMS)
    quota_headers = ScopusHeaders(**RAW_HEADERS_OK)
    res = json_response(params, quota_headers, [{"any": "any"}])
    body: Json = json.loads(res.body.decode())  # type: ignore

    assert "application/json" in res.headers["Content-Type"]
    assert res.headers["X-API-Key"] == API_KEY
    assert res.headers["X-Keywords"]
    assert res.headers["X-Search-Limit"]
    assert res.headers["X-Search-Remaining"]
    assert res.headers["X-Search-Reset"]
    assert body["success"] and body["status_code"] == HTTP_200
    assert "Combination totals survey successfully" in body["message"]
    assert body["result"]["combinations"][0]["any"] == "any"
