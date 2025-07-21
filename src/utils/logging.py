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


class Prefix(StrEnum):
    TRACE = "\033[34mTRACE\033[m:".ljust(17)
    DEBUG = "\033[35mDEBUG\033[m:".ljust(17)
    INFO = "\033[32mINFO\033[m:".ljust(17)
    QUOTA = "\033[35mQUOTA\033[m:".ljust(17)
    ERROR = "\033[31mERROR\033[m:".ljust(17)
    EXCEPTION = "\033[31mEXCEPTION\033[m:".ljust(17)
    SEARCH = "\033[36mSEARCH\033[m:".ljust(17)
    ABSTRACT = "\033[36mABSTRACT\033[m:".ljust(17)


class ANSIFormatter(Formatter):
    def format(self, record) -> str:
        message = super().format(record)
        return sub(ANSI_ESCAPE_PATTERN, "", message)


class LogRequest:
    """HTTP request details for logging"""

    __METHOD = "GET"

    def __init__(self, url: str) -> None:
        self.client = None
        self.method = self.__METHOD
        self.url = url


class Logging:
    """Configure and customize application logging"""

    __METHOD_COLOR = {"GET": "94", "POST": "92", "PUT": "93", "DELETE": "91"}
    __QUOTA = (
        "Limit: \033[33m{limit}\033[m. Remaining: \033[33m{remaining}\033[m"
        ". Reset: \033[33m{reset}\033[m. ELS-Status: \033[{color}m{status}"
    )
    __TRACE = (
        "[\033[36m{host}\033[m:\033[36m{port}\033[m] \033[{method_color}m"
        "{method} \033[37;1m{url}\033[m \033[{status_color}m{code} "
        "{status_phrase} \033[m{time:.2f}s"
    )
    __COMBINATIONS = (
        "Keywords: \033[33m{keywords}\033[m. Combinations: \033[33m"
        "{combinations}\033[m. Total-Sum: \033[33m{total:,}\033[m. "
        "Average-Found: \033[33m~{average:,}"
    )
    __LOSS = (
        "Initial: \033[33m{initial}\033[m. Final: \033[33m{final}\033[m"
        ". Loss: \033[33m{loss:.2f}%"
    )
    __EXCEPTION = "{module}.{qualname}: {filepath}, line {line}, col {col}"
    __UVICORN_FMT = "%(asctime)s %(levelprefix)s %(message)s"
    __FRAME = FrameSummary(__file__, 1, "<logging>", colno=0)
    __STATUS_COLOR = {2: "32", 3: "33", 4: "31", 5: "31"}
    __LOGGER_NAME = "scopus.survey.api"
    __FMT = "%(asctime)s %(message)s"
    __DATEFMT = "%Y-%m-%d %H:%M:%S"
    __HIDE_API_KEY = "apiKey=..."
    __DIR = Path(".logs")
    __PERCENT = 100

    def __init__(self, params: LogParams) -> None:
        """Configure and customize application logging"""
        self.__logger = getLogger(self.__LOGGER_NAME)
        self.__params = params

        formater = {"fmt": self.__UVICORN_FMT, "datefmt": self.__DATEFMT}
        LOGGING_CONFIG["formatters"]["default"].update(formater)

        formatter = Formatter(self.__FMT, self.__DATEFMT)
        self.__stream_handler = StreamHandler(stream=stdout)
        self.__stream_handler.setFormatter(formatter)
        self.__logger.addHandler(self.__stream_handler)

        if self.__params.logging_file:
            self.__DIR.mkdir(parents=True, exist_ok=True)
            filename = self.__DIR / "records_0.log"

            file_handler = RotatingFileHandler(
                filename=filename,
                mode="a",
                maxBytes=512000,
                backupCount=15,
                encoding="utf-8",
            )

            file_handler.namer = self.__namer
            ansi_formatter = ANSIFormatter(self.__FMT, self.__DATEFMT)
            file_handler.setFormatter(ansi_formatter)

            getLogger("uvicorn").addHandler(file_handler)
            self.__logger.addHandler(file_handler)

    def __namer(self, default_filename: str) -> str:
        filename = Path(default_filename)
        log_count = filename.suffixes[1].removeprefix(".")
        new_name = filename.with_name(f"records_{log_count}.log")
        return new_name.as_posix()

    @property
    def logger(self) -> list[Logger]:
        return [self.__logger]

    @staticmethod
    def error_message(exc: Exception, message: str = None) -> str:
        if exc.args and exc.args[0] and isinstance(exc.args[0], str):
            return exc.args[0]
        if message is not None:
            return message
        return repr(exc)

    def info(self, message: str) -> None:
        self.__logger.setLevel(INFO)
        self.__logger.info("%s %s\033[m", Prefix.INFO, message)

    def loss(self, initial: int, final: int) -> None:
        message = self.__LOSS.format(
            initial=initial,
            final=final,
            loss=(initial / final) * self.__PERCENT,
        )
        self.info(message)

    def combinations(self, keywords: int, bundles: list[Json]) -> None:
        totals: list[int] = [data["total"] for data in bundles]
        average = 0.0

        if sum(totals) > 0:
            square_totals_sum = sum(total * total for total in totals)
            average = square_totals_sum / (keywords * sum(totals))

        message = self.__COMBINATIONS.format(
            keywords=keywords,
            combinations=len(bundles),
            total=sum(totals),
            average=int(average),
        )
        self.info(message)

    def quota(self, quota: Quota, code: int) -> None:
        if quota.status.startswith(NO_RESULTS):
            code = HTTPStatus.NOT_FOUND.value

        message = self.__QUOTA.format(
            limit=quota.limit,
            remaining=quota.remaining,
            reset=quota.reset_datetime,
            color=self.__STATUS_COLOR[(code // 100)],
            status=quota.status,
        )
        self.__logger.setLevel(INFO)
        self.__logger.info("%s %s\033[m", Prefix.QUOTA, message)

    def error(self, message: str, exc: Exception = None) -> None:
        if exc is not None:
            message = self.error_message(exc, message)

        self.__logger.setLevel(ERROR)
        self.__logger.error("%s \033[31m%s\033[m", Prefix.ERROR, message)

    def debug(self, data: dict) -> None:
        if self.__params.debug:
            self.__logger.setLevel(DEBUG)
            self.__logger.debug(
                "%s \033[33mJSON:\033[m %s", Prefix.DEBUG, dumps(data)
            )

    def exception(self, exception: Exception) -> None:
        traceback = exc_info()[2]
        frame = extract_tb(traceback)[-1] if traceback else self.__FRAME

        message = self.__EXCEPTION.format(
            module=type(exception).__module__,
            qualname=type(exception).__qualname__,
            filepath=frame.filename,
            line=frame.lineno,
            col=frame.colno,
        )

        self.__logger.setLevel(ERROR)
        self.__logger.exception(
            "%s \033[31m%s\033[m",
            Prefix.EXCEPTION,
            message,
            exc_info=True,
        )

    def __trace(
        self,
        log_prefix: Prefix,
        request: Request | LogRequest,
        code: int,
        time: float,
    ) -> None:
        if request.client is None:
            host, port = self.__params.host, self.__params.port
        else:
            host, port = request.client.host, request.client.port

        message = self.__TRACE.format(
            host=host,
            port=port,
            method_color=self.__METHOD_COLOR.get(request.method, "90"),
            method=request.method,
            url=request.url,
            status_color=self.__STATUS_COLOR[(code // 100)],
            code=code,
            status_phrase=HTTPStatus(code).phrase,
            time=time,
        )

        self.__logger.setLevel(INFO)
        self.__logger.info("%s %s\033[m", log_prefix, message)

    def trace(self, request: Request, code: int, time: float) -> None:
        self.__trace(Prefix.TRACE, request, code, time)

    def api_call(self, url: str, code: int, time: float) -> None:
        if url.startswith(SEARCH_API_URL):
            log_prefix = Prefix.SEARCH
        else:
            log_prefix = Prefix.ABSTRACT
        url = sub(API_KEY_LOG_PATTERN, self.__HIDE_API_KEY, url)
        self.__trace(log_prefix, LogRequest(url), code, time)
