from http import HTTPStatus
from json import loads
from typing import Any

from pytest import ExceptionInfo, fixture

from src.adapters.presenters.error_response import ErrorJSON, ErrorResponse
from src.core.common.types import Json
from src.core.domain.http_exceptions import HTTPError
from tests.helpers.models import Request


@fixture(scope="session")
def session_data():
    data = {"code": "None"}
    yield data


@fixture(scope="session", autouse=True)
def lifespan():
    print("\033[93mPytest Session Start\033[m", flush=True)
    yield
    print("\033[93mPytest Session Finish\033[m", flush=True)


def assert_http_error(
    error: ExceptionInfo[HTTPError],
    code: int,
    message: str,
    errors: bool = True,
) -> None:
    assert error.value.status == HTTPStatus(code)
    assert error.value.message == message
    assert error.value.status_code == code
    assert error.value.detail

    if errors:
        assert error.value.errors is not None
    else:
        assert error.value.errors is None


def assert_error_response(
    response: ErrorJSON,
    code: int,
    message: str,
    errors: None | Any = None,
) -> None:
    data: Json = loads(response.body.decode())  # type: ignore

    if data.get("request"):
        data["request"] = Request()
    model = ErrorResponse.model_validate(data)

    assert not model.success and model.timestamp and model.request
    assert model.status_code == HTTPStatus(code).value
    assert model.status == HTTPStatus(code).phrase
    assert model.message == message

    if errors is None:
        assert not model.errors
    else:
        assert model.errors == errors
