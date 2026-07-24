# pylint: disable=W0621
import logging
import os
import re
import sys
import traceback
from datetime import datetime
from enum import IntEnum
from http import HTTPStatus
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

import gunicorn.glogging
import uvicorn.logging
from fastapi.requests import Request as FastAPIRequest
from pydantic_core import to_jsonable_python
from starlette.types import Scope as StarletteScope
from tqdm.std import tqdm as std_tqdm

from src.core.domain.types import APIName, Json, ScopusHeaders
from src.infra.config.config import ENV
from src.infra.config.scopus import SEARCH_API_URL


# e.g. \033[35;1m, \033[m
_ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9\;]*m")

# e.g. apiKey=6bd9327547a3cf4c56586324df4b7d92  (Random Hash)
_API_KEY_PARAM_PATTERN = re.compile(r"apiKey\=[a-zA-Z0-9]{32}")


def _filename(count: int) -> str:
    return f"log_{count}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log"


_CHROME_DEVTOOLS_URL = ".well-known/appspecific/com.chrome.devtools.json"
_LIVERELOAD_ROUTE = "/livereload"


def excluded_routes(path: str) -> bool:
    is_devtools = path.endswith(_CHROME_DEVTOOLS_URL)
    is_livereload = path.count(_LIVERELOAD_ROUTE) == 1
    return is_devtools and is_livereload


class _Level(IntEnum):
    TRACE = 21
    DEBUG = 10
    INFO = 20
    QUOTA = 22
    ERROR = 40
    EXCEPTION = 41
    SEARCH = 23
    ABSTRACT = 24
    WARNING = 30


class _ANSIFormatter(logging.Formatter):

    _LEVEL_COLOR = {
        _Level.TRACE: "34",
        _Level.DEBUG: "35",
        _Level.INFO: "32",
        _Level.QUOTA: "35",
        _Level.ERROR: "31",
        _Level.EXCEPTION: "31",
        _Level.SEARCH: "36",
        _Level.ABSTRACT: "36",
        _Level.WARNING: "33",
    }

    def __init__(self, fmt: str, datefmt: str, strip_ansi: bool):
        super().__init__(fmt, datefmt)
        self._strip_ansi = strip_ansi

        if os.environ.get("PYTEST_VERSION") is None:
            self._color_supported = sys.stdout.isatty()
        else:
            self._color_supported = True

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()

        if not self._color_supported or self._strip_ansi:
            log_message = super().format(record)
            return _ANSI_ESCAPE_PATTERN.sub("", log_message)

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

    def _namer(self, path: str) -> str:
        # From file.log.1 to file_1.log
        count = int(Path(path).suffixes[1].removeprefix("."))
        return Path(path).with_name(_filename(count)).as_posix()


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
_UVICORN_FMT = "%(asctime)s %(levelprefix)-19s %(message)s"
_FRAME = traceback.FrameSummary(
    filename=__file__, lineno=1, name="<logging>", colno=1
)
_STATUS_COLOR = {2: "32", 3: "33", 4: "31", 5: "31"}
_FMT = "%(asctime)s %(levelname)-18s %(message)s"
_FILENAME = Path(f".logs/{_filename(0)}")
_LOGGER_NAME = "scopus.survey.api"
_DATEFMT = "%Y-%m-%d %H:%M:%S"  # e.g. 2026-01-01 00:00:00

TEST_FORMATTER = _ANSIFormatter(fmt=_FMT, datefmt=_DATEFMT, strip_ansi=False)

_FILE_HANDLER: Json = {
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
            "()": _ANSIFormatter,
            "format": _FMT,
            "datefmt": _DATEFMT,
            "strip_ansi": False,
        },
        "ansi_cleaner": {
            "()": _ANSIFormatter,
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
            "level": logging.DEBUG if ENV.debug else logging.INFO,
        }
    },
}
UVICORN_LOGGING_CONFIG: Json = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": uvicorn.logging.DefaultFormatter,
            "fmt": _UVICORN_FMT,
            "datefmt": _DATEFMT,
            "use_colors": True,
        },
        "access": {},
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": logging.StreamHandler,
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {"level": "INFO"},
    },
}


if ENV.logging_file:
    _FILENAME.parent.mkdir(exist_ok=True)
    _LOGGING_CONFIG["handlers"].setdefault("file", _FILE_HANDLER)
    _LOGGING_CONFIG["root"]["handlers"].append("file")
    UVICORN_LOGGING_CONFIG["handlers"].setdefault("file", _FILE_HANDLER)
    UVICORN_LOGGING_CONFIG["loggers"]["uvicorn"]["handlers"].append("file")

logging.addLevelName(_Level.TRACE, _Level.TRACE.name)
logging.addLevelName(_Level.QUOTA, _Level.QUOTA.name)
logging.addLevelName(_Level.SEARCH, _Level.SEARCH.name)
logging.addLevelName(_Level.ABSTRACT, _Level.ABSTRACT.name)
logging.addLevelName(_Level.EXCEPTION, _Level.EXCEPTION.name)

dictConfig(_LOGGING_CONFIG)
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
_GUNICORN_RUNNING = (
    "Gunicorn running at\033[37;1m http://localhost:%d"
    "\033[m (Press CTRL+C to quit)\033[m"
)
_LOCALHOST_ACCESS = "Please access at \033[37;1mhttp://localhost:%d\033[m"
_TRY_AGAIN = "Please try again on \033[37;1m%s\033[m"
_TOTAL_FOUND = "Total Found: \033[33m%d\033[m"


def info(message: str) -> None:
    LOGGER.info("%s\033[m", message, stacklevel=2)


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


def quota(headers: ScopusHeaders, api_name: APIName) -> None:
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


def gunicorn_running(port: int) -> None:
    LOGGER.info(_GUNICORN_RUNNING, port, stacklevel=2)


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


def debug(data: Json) -> None:
    LOGGER.debug(
        "\033[33mJSON:\033[m %s\033[m",
        to_jsonable_python(data, fallback=repr),
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
        "url": _API_KEY_PARAM_PATTERN.sub("apiKey=...", str(req.url)),
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
    _trace(_Level.TRACE, req, code, duration)


def api_call(url: str, code: int, time: float) -> None:
    if url.startswith(SEARCH_API_URL):
        prefix = _Level.SEARCH
    else:
        prefix = _Level.ABSTRACT

    scope: StarletteScope = {  # type: ignore
        "type": "http",
        "method": "GET",
        "path": url,
        "headers": {},
    }
    _trace(prefix, FastAPIRequest(scope), code, f"{time:.2f}s")


class ProdLogger(gunicorn.glogging.Logger):
    error_fmt = r"%(asctime)s %(levelname)-10s %(message)s"
    datefmt = r"%Y-%m-%d %H:%M:%S"  # e.g. 2026-01-01 00:00:00
    access_fmt = ""

    def access(self, resp, req, environ, request_time):
        pass
