import logging
import logging.config
import os
import re
import sys
import traceback
from datetime import datetime
from enum import IntEnum
from http import HTTPStatus
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from fastapi.requests import Request as FastAPIRequest
from pandas import DataFrame
from pydantic import BaseModel, TypeAdapter, ValidationError
from pydantic_core import to_jsonable_python
from starlette.types import Scope as StarletteScope
from tqdm.std import tqdm as std_tqdm

from src.core.domain.types import Json, ScopusHeaders, mask_secret
from src.infra.config.config import ENV
from src.infra.config.scopus import EMPTY_RESULT
from src.infra.types import APIName


def is_noisy_access(path: str) -> bool:
    return "devtools" in path or "livereload" in path


class _Level(IntEnum):
    DEBUG = 10
    API_CALL = 15  # Search & Abstract API calls
    INFO = 20
    ACCESS = 21  # HTTP request/response summary
    QUOTA = 22  # API Key quota consumption
    WARNING = 30
    ERROR = 40
    EXCEPTION = 41


class ANSIFormatter(logging.Formatter):

    # e.g. \033[35;1m, \033[m
    _ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9\;]*m")
    _BOOLEAN_ADAPTER = TypeAdapter(bool)
    _LEVEL_COLOR = {
        _Level.DEBUG: "35",
        _Level.API_CALL: "36",
        _Level.INFO: "32",
        _Level.ACCESS: "34",
        _Level.QUOTA: "35",
        _Level.WARNING: "33",
        _Level.ERROR: "31",
        _Level.EXCEPTION: "31",
    }

    def __init__(self, fmt: str, datefmt: str, strip_ansi: bool):
        super().__init__(fmt, datefmt)
        self._strip_ansi = strip_ansi
        self._color_supported = self._should_enable_colors()

    def _get_env_option(self, env_name: str) -> bool | None:
        value = os.environ.get(env_name)
        if value is not None and value.strip() != "":
            try:
                return self._BOOLEAN_ADAPTER.validate_python(value)
            except ValidationError:
                pass
        return None

    def _should_enable_colors(self) -> bool:
        # Universal standard (Highest Priority)
        if os.environ.get("NO_COLOR"):
            return False

        # Universal CLI override
        force_color = self._get_env_option("FORCE_COLOR")
        if force_color is not None:
            return force_color

        # Python ecosystem override
        py_colors = self._get_env_option("PY_COLORS")
        if py_colors is not None:
            return py_colors

        # Test Runner Environments (VS Code Test Results & Pytest)
        is_vscode_pytest = any("vscode_pytest" in arg for arg in sys.argv)
        if is_vscode_pytest or os.environ.get("PYTEST_VERSION") is not None:
            return True

        # Default TTY Check
        return sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()

        if not self._color_supported or self._strip_ansi:
            log_message = super().format(record)
            return self._ANSI_ESCAPE_RE.sub("", log_message)

        levelname, message = record.levelname, record.message

        try:
            color = self._LEVEL_COLOR[_Level[levelname]]
            record.levelname = f"\033[{color}m{levelname}\033[m:"
            record.message = f"\033[m{message}\033[m"

            return super().format(record)
        finally:
            record.levelname = levelname
            record.message = message


class _FileHandler(RotatingFileHandler):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.namer = self._namer

    @classmethod
    def filename(cls, count: int) -> str:
        return f"log_{count}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log"

    def _namer(self, path: str) -> str:
        # From file.log.1 to file_1.log
        count = int(Path(path).suffixes[1].removeprefix("."))
        return Path(path).with_name(self.filename(count)).as_posix()


class _TQDMLoggingHandler(logging.StreamHandler):

    def __init__(self, stream: Any = None) -> None:
        super().__init__(stream)
        self.tqdm_class = std_tqdm

    def emit(self, record) -> None:
        try:
            msg = self.format(record)
            self.tqdm_class.write(msg, file=self.stream)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:  # noqa pylint: disable=bare-except
            self.handleError(record)


_METHOD_COLOR = {"GET": "94", "POST": "92", "PUT": "93", "DELETE": "91"}
_FRAME = traceback.FrameSummary(
    filename=__file__, lineno=1, name="<logging>", colno=1
)
_STATUS_COLOR = {2: "32", 3: "33", 4: "31", 5: "31"}
_FMT = "%(asctime)s %(levelname)-18s %(message)s"
_FILENAME = Path(f".logs/{_FileHandler.filename(0)}")
_LOGGER_NAME = "scopus.survey.api"
_DATEFMT = "%Y-%m-%d %H:%M:%S"  # e.g. 2026-01-01 00:00:00

FILE_HANDLER: Json = {
    "()": _FileHandler,
    "formatter": "ansi_cleaner",
    "filename": _FILENAME,
    "mode": "a",
    "maxBytes": 10485760,  # 10MB
    "backupCount": 15,  # 15 files
    "encoding": "utf-8",
}
_LOGGING_CONFIG: Json = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": ANSIFormatter,
            "format": _FMT,
            "datefmt": _DATEFMT,
            "strip_ansi": False,
        },
        "ansi_cleaner": {
            "()": ANSIFormatter,
            "fmt": _FMT,
            "datefmt": _DATEFMT,
            "strip_ansi": True,
        },
    },
    "handlers": {
        "console": {
            "class": (
                _TQDMLoggingHandler
                if ENV.progress_bar
                else logging.StreamHandler
            ),
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        _LOGGER_NAME: {
            "handlers": ["console"],
            "level": _Level[ENV.log_level],
        }
    },
}


if ENV.logging_file:
    _FILENAME.parent.mkdir(exist_ok=True)
    _LOGGING_CONFIG["handlers"]["file"] = FILE_HANDLER
    _LOGGING_CONFIG["root"]["handlers"].append("file")

logging.addLevelName(_Level.API_CALL, _Level.API_CALL.name)
logging.addLevelName(_Level.ACCESS, _Level.ACCESS.name)
logging.addLevelName(_Level.QUOTA, _Level.QUOTA.name)
logging.addLevelName(_Level.EXCEPTION, _Level.EXCEPTION.name)

logging.config.dictConfig(_LOGGING_CONFIG)
LOGGER = logging.getLogger(_LOGGER_NAME)


_QUOTA = (
    "Scopus API: \033[32m%(api_name)s\033[m. Limit: \033[33m%(limit)s\033[m. "
    "Remaining: \033[33m%(remaining)s\033[m. Reset: \033[33m%(reset)s"
    "\033[m. ELS-Status: \033[33m%(status)s\033[m"
)
_TRACE = (
    "[\033[36m%(host)s\033[m:\033[36m%(port)d\033[m] \033[%(method_color)sm"
    "%(method)s \033[37;1m%(url)s\033[m \033[%(status_color)sm%(code)d "
    "%(status_phrase)s \033[m%(time)s\033[m"
)
_COMBINATIONS = (
    "Keywords: \033[33m%(keywords)d\033[m. Combinations: \033[33m"
    "%(combinations)d\033[m"
)
_LOSS = (
    "Initial: \033[33m%(initial)d\033[m. Final: \033[33m%(final)d"
    "\033[m. Loss: \033[33m%(loss_amount)d \033[m(\033[33m"
    "%(loss_percent).2f%%\033[m)"
)
_EXCEPTION = (
    '\033[31m%(qualname)s\033[m: File "%(filepath)s", line %(line)d, col '
    "%(col)d, from \033[31m%(module)s.%(qualname)s\033[m"
)
_PROD_CONFIG = (
    "Active Configuration (Production-only Forced Overrides Applied): %s\033[m"
)
_GUNICORN_RUNNING = (
    "Gunicorn running at\033[37;1m http://localhost:%d"
    "\033[m (Press CTRL+C to quit)\033[m"
)
_LOCALHOST_ACCESS = "Please access at \033[37;1mhttp://localhost:%d\033[m"
_TRY_AGAIN = "Please try again on \033[37;1m%s\033[m"
_BATCH_TO_FETCH = "Batch of \033[33m%d\033[m requests to fetch"
_BATCH_COMPLETED = "Batch completed in \033[33m%s\033[m"
_TOTAL_FOUND = "Total Found: \033[33m%d\033[m"


def info(message: str) -> None:
    LOGGER.info("%s\033[m", message, stacklevel=2)


def batch_to_fetch(progress: range) -> None:
    LOGGER.info(
        _BATCH_TO_FETCH, (progress.stop - progress.start), stacklevel=2
    )


def batch_completed(process_time: float) -> None:
    if process_time > 60.0:
        minutes = process_time / 60.0
        duration = f"{process_time:.2f}s ({minutes:.2f}m)"
    else:
        duration = f"{process_time:.2f}s"
    LOGGER.info(_BATCH_COMPLETED, duration, stacklevel=2)


def loss(initial: int, final: int) -> None:
    loss_value = initial - final
    loss_percent = 0.0 if loss_value == 0 else (loss_value / initial) * 100.0
    args = {
        "initial": initial,
        "final": final,
        "loss_amount": loss_value,
        "loss_percent": loss_percent,
    }
    LOGGER.info(_LOSS, args, stacklevel=2)


def combinations(keywords_count: int) -> None:
    args = {
        "keywords": keywords_count,
        "combinations": 2**keywords_count - 1,
    }
    LOGGER.info(_COMBINATIONS, args, stacklevel=2)


def quota(
    headers: ScopusHeaders, api_name: APIName, allow_empty: bool = None
) -> None:
    if allow_empty and headers.status and EMPTY_RESULT in headers.status:
        headers.status = "OK"

    args = {
        "api_name": api_name.capitalize(),
        "limit": headers.limit,
        "remaining": headers.remaining,
        "reset": headers.reset_datetime,
        "status": headers.status,
    }
    LOGGER.log(_Level.QUOTA, _QUOTA, args, stacklevel=2)


def try_again(reset: str) -> None:
    LOGGER.info(_TRY_AGAIN, reset, stacklevel=2)


def localhost(port: int) -> None:
    LOGGER.info(_LOCALHOST_ACCESS, port, stacklevel=2)


def total_found(total_results: int) -> None:
    LOGGER.info(_TOTAL_FOUND, total_results, stacklevel=2)


def gunicorn_running(env_config: Json) -> None:
    prod_config = to_jsonable_python(env_config, fallback=repr)
    LOGGER.info(_PROD_CONFIG, prod_config, stacklevel=2)
    LOGGER.info(_GUNICORN_RUNNING, env_config["port"], stacklevel=2)


def error(message: str, tracking_id: str = None) -> None:
    if tracking_id:
        LOGGER.error(
            "\033[31m%s\033[m [ID:\033[36m%s\033[m]",
            message,
            tracking_id,
            stacklevel=2,
        )
    else:
        LOGGER.error("\033[31m%s\033[m", message, stacklevel=2)


def debug(**kwargs) -> None:
    if not LOGGER.isEnabledFor(logging.DEBUG):
        return

    for key, value in kwargs.items():
        if isinstance(value, BaseModel):
            kwargs[key] = value.model_dump()
        if isinstance(value, DataFrame):
            kwargs[key] = value.to_dict(orient="records")

    LOGGER.debug(
        "\033[m%s\033[m",
        to_jsonable_python(kwargs, fallback=repr),
        stacklevel=2,
    )


def exception(exc: Exception) -> None:
    exc_trace = sys.exc_info()[2]
    frame = traceback.extract_tb(exc_trace)[-1] if exc_trace else _FRAME

    args = {
        "module": type(exc).__module__,
        "qualname": type(exc).__qualname__,
        "filepath": frame.filename,
        "line": frame.lineno if frame.lineno else 1,
        "col": frame.colno if frame.colno else 1,
    }
    LOGGER.log(_Level.EXCEPTION, _EXCEPTION, args, exc_info=True, stacklevel=2)


# e.g. apiKey=6bd9327547a3cf4c56586324df4b7d92  (Random Hash)
_API_KEY_PARAM_RE = re.compile(r"apiKey\=([a-zA-Z0-9]{32})")


def _mask_api_key_param(match: re.Match[str]) -> str:
    return f"apiKey={mask_secret(match.group(1))}"


def _trace(
    prefix: _Level,
    req: FastAPIRequest,
    code: int,
    time: str,
) -> None:
    if req.client is None:
        host, port = ENV.host, ENV.port
    else:
        host, port = req.client.host, req.client.port

    args = {
        "host": host,
        "port": port,
        "method_color": _METHOD_COLOR.get(req.method, "90"),
        "method": req.method,
        "url": _API_KEY_PARAM_RE.sub(_mask_api_key_param, str(req.url)),
        "status_color": _STATUS_COLOR[(code // 100)],
        "code": code,
        "status_phrase": HTTPStatus(code).phrase,
        "time": time,
    }
    LOGGER.log(prefix, _TRACE, args, stacklevel=3)


def trace(req: FastAPIRequest, code: int, process_time: float) -> None:
    if process_time > 60.0:
        minutes = process_time / 60.0
        duration = f"{process_time:.2f}s ({minutes:.2f}m)"
    else:
        duration = f"{process_time:.2f}s"
    _trace(_Level.ACCESS, req, code, duration)


def api_call(url: str, code: int, time: float) -> None:
    scope: StarletteScope = {
        "type": "http",
        "method": "GET",
        "path": url,
        "headers": {},
    }
    _trace(_Level.API_CALL, FastAPIRequest(scope), code, f"{time:.2f}s")
