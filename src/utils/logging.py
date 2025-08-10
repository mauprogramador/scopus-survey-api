from enum import StrEnum
from http import HTTPStatus
from json import dumps
from logging import (
    DEBUG,
    ERROR,
    INFO,
    Formatter,
    Logger,
    StreamHandler,
    getLogger,
)
from logging.handlers import RotatingFileHandler
from pathlib import Path
from re import sub
from sys import exc_info, stdout
from traceback import FrameSummary, extract_tb

from fastapi import Request
from uvicorn.config import LOGGING_CONFIG

from src.core.common.patterns import ANSI_ESCAPE_PATTERN, API_KEY_LOG_PATTERN
from src.core.common.types import Json, LogParams, Quota
from src.core.config.scopus import NO_RESULTS, SEARCH_API_URL


class _Prefix(StrEnum):
    TRACE = "\033[34mTRACE\033[m:".ljust(17)
    DEBUG = "\033[35mDEBUG\033[m:".ljust(17)
    INFO = "\033[32mINFO\033[m:".ljust(17)
    QUOTA = "\033[35mQUOTA\033[m:".ljust(17)
    ERROR = "\033[31mERROR\033[m:".ljust(17)
    EXCEPTION = "\033[31mEXCEPTION\033[m:".ljust(17)
    SEARCH = "\033[36mSEARCH\033[m:".ljust(17)
    ABSTRACT = "\033[36mABSTRACT\033[m:".ljust(17)


class _ANSIFormatter(Formatter):
    def format(self, record) -> str:
        message = super().format(record)
        return sub(ANSI_ESCAPE_PATTERN, "", message)


class _LogRequest:
    """HTTP request details for logging"""

    _METHOD = "GET"

    def __init__(self, url: str) -> None:
        self.client = None
        self.method = self._METHOD
        self.url = url


class Logging:
    """Configure and customize application logging"""

    _METHOD_COLOR = {"GET": "94", "POST": "92", "PUT": "93", "DELETE": "91"}
    _QUOTA = (
        "Limit: \033[33m{limit}\033[m. Remaining: \033[33m{remaining}\033[m"
        ". Reset: \033[33m{reset}\033[m. ELS-Status: \033[{color}m{status}"
    )
    _TRACE = (
        "[\033[36m{host}\033[m:\033[36m{port}\033[m] \033[{method_color}m"
        "{method} \033[37;1m{url}\033[m \033[{status_color}m{code} "
        "{status_phrase} \033[m{time:.2f}s"
    )
    _COMBINATIONS = (
        "Keywords: \033[33m{keywords}\033[m. Combinations: \033[33m"
        "{combinations}\033[m. Total-Sum: \033[33m{total:,}\033[m. "
        "Average-Found: \033[33m~{average:,}"
    )
    _LOSS = (
        "Initial: \033[33m{initial}\033[m. Final: \033[33m{final}\033[m"
        ". Loss: \033[33m{loss:.2f}%"
    )
    _EXCEPTION = "{module}.{qualname}: {filepath}, line {line}, col {col}"
    _UVICORN_FMT = "%(asctime)s %(levelprefix)s %(message)s"
    _FRAME = FrameSummary(__file__, 1, "<logging>", colno=0)
    _STATUS_COLOR = {2: "32", 3: "33", 4: "31", 5: "31"}
    _LOGGER_NAME = "scopus.survey.api"
    _FMT = "%(asctime)s %(message)s"
    _DATEFMT = "%Y-%m-%d %H:%M:%S"
    _HIDE_API_KEY = "apiKey=..."
    _DIR = Path(".logs")

    def __init__(self, params: LogParams) -> None:
        """Configure and customize application logging"""
        self._logger = getLogger(self._LOGGER_NAME)
        self._params = params

        formater = {"fmt": self._UVICORN_FMT, "datefmt": self._DATEFMT}
        LOGGING_CONFIG["formatters"]["default"].update(formater)

        formatter = Formatter(self._FMT, self._DATEFMT)
        self._stream_handler = StreamHandler(stream=stdout)
        self._stream_handler.setFormatter(formatter)
        self._logger.addHandler(self._stream_handler)

        if self._params.logging_file:
            self._DIR.mkdir(parents=True, exist_ok=True)
            filename = self._DIR / "records_0.log"

            file_handler = RotatingFileHandler(
                filename=filename,
                mode="a",
                maxBytes=512000,
                backupCount=15,
                encoding="utf-8",
            )

            file_handler.namer = self._namer
            ansi_formatter = _ANSIFormatter(self._FMT, self._DATEFMT)
            file_handler.setFormatter(ansi_formatter)

            getLogger("uvicorn").addHandler(file_handler)
            self._logger.addHandler(file_handler)

    def _namer(self, default_filename: str) -> str:
        filename = Path(default_filename)
        log_count = filename.suffixes[1].removeprefix(".")
        new_name = filename.with_name(f"records_{log_count}.log")
        return new_name.as_posix()

    @property
    def logger(self) -> list[Logger]:
        return [self._logger]

    @staticmethod
    def error_message(exc: Exception, message: str = None) -> str:
        if exc.args and exc.args[0] and isinstance(exc.args[0], str):
            return exc.args[0]
        if message is not None:
            return message
        return repr(exc)

    def info(self, message: str) -> None:
        self._logger.setLevel(INFO)
        self._logger.info("%s %s\033[m", _Prefix.INFO, message)

    def loss(self, initial: int, final: int, loss: float) -> None:
        message = self._LOSS.format(
            initial=initial,
            final=final,
            loss=loss,
        )
        self.info(message)

    def combinations(self, keywords: int, bundles: list[Json]) -> None:
        totals: list[int] = [data["total"] for data in bundles]
        average = 0.0

        if sum(totals) > 0:
            square_totals_sum = sum(total * total for total in totals)
            average = square_totals_sum / (keywords * sum(totals))

        message = self._COMBINATIONS.format(
            keywords=keywords,
            combinations=len(bundles),
            total=sum(totals),
            average=int(average),
        )
        self.info(message)

    def quota(self, quota: Quota, code: int) -> None:
        if quota.status.startswith(NO_RESULTS):
            code = HTTPStatus.NOT_FOUND.value

        message = self._QUOTA.format(
            limit=quota.limit,
            remaining=quota.remaining,
            reset=quota.reset_datetime,
            color=self._STATUS_COLOR[(code // 100)],
            status=quota.status,
        )
        self._logger.setLevel(INFO)
        self._logger.info("%s %s\033[m", _Prefix.QUOTA, message)

    def error(self, message: str, exc: Exception = None) -> None:
        if exc is not None:
            message = self.error_message(exc, message)

        self._logger.setLevel(ERROR)
        self._logger.error("%s \033[31m%s\033[m", _Prefix.ERROR, message)

    def debug(self, data: dict) -> None:
        if self._params.debug:
            self._logger.setLevel(DEBUG)
            self._logger.debug(
                "%s \033[33mJSON:\033[m %s", _Prefix.DEBUG, dumps(data)
            )

    def exception(self, exception: Exception) -> None:
        traceback = exc_info()[2]
        frame = extract_tb(traceback)[-1] if traceback else self._FRAME

        message = self._EXCEPTION.format(
            module=type(exception).__module__,
            qualname=type(exception).__qualname__,
            filepath=frame.filename,
            line=frame.lineno,
            col=frame.colno,
        )

        self._logger.setLevel(ERROR)
        self._logger.exception(
            "%s \033[31m%s\033[m",
            _Prefix.EXCEPTION,
            message,
            exc_info=True,
        )

    def _trace(
        self,
        log_prefix: _Prefix,
        request: Request | _LogRequest,
        code: int,
        time: float,
    ) -> None:
        if request.client is None:
            host, port = self._params.host, self._params.port
        else:
            host, port = request.client.host, request.client.port

        message = self._TRACE.format(
            host=host,
            port=port,
            method_color=self._METHOD_COLOR.get(request.method, "90"),
            method=request.method,
            url=request.url,
            status_color=self._STATUS_COLOR[(code // 100)],
            code=code,
            status_phrase=HTTPStatus(code).phrase,
            time=time,
        )

        self._logger.setLevel(INFO)
        self._logger.info("%s %s\033[m", log_prefix, message)

    def trace(self, request: Request, code: int, time: float) -> None:
        self._trace(_Prefix.TRACE, request, code, time)

    def api_call(self, url: str, code: int, time: float) -> None:
        if url.startswith(SEARCH_API_URL):
            log_prefix = _Prefix.SEARCH
        else:
            log_prefix = _Prefix.ABSTRACT
        url = sub(API_KEY_LOG_PATTERN, self._HIDE_API_KEY, url)
        self._trace(log_prefix, _LogRequest(url), code, time)
