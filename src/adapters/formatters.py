from pydantic import ValidationError

from src.core.domain.types import Json


def _get_error_message(exc: Exception) -> str:
    if getattr(exc, "message", None) is not None:
        return getattr(exc, "message")
    if getattr(exc, "detail", None) is not None:
        return getattr(exc, "detail")
    if exc.args and exc.args[0] and isinstance(exc.args[0], str):
        return exc.args[0]
    return repr(exc)


def _get_error_details(exc: Exception) -> Json:
    details = {
        "type": f"{type(exc).__module__}.{type(exc).__qualname__}",
        "message": _get_error_message(exc),
    }

    if isinstance(exc, ValidationError):
        pydantic_errors = exc.errors(include_url=False)
        details["message"] = pydantic_errors[0].get("msg", exc.title)
        details["errors"] = pydantic_errors

    return details


def get_error_details(exc: Exception) -> Json:
    details = _get_error_details(exc)

    cause = exc.__cause__ or exc.__context__
    if cause:
        details["cause"] = _get_error_details(cause)

    return details
