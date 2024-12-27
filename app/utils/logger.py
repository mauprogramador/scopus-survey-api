from datetime import datetime
from http import HTTPStatus
from json import dumps
from logging import (
    DEBUG,
    ERROR,
    INFO,
    FileHandler,
    Filter,
    Formatter,
    Logger,
    LogRecord,
    StreamHandler,
    getLogger,
)
from os import mkdir
from os.path import exists
from re import compile as regex_compile

from fastapi import Request as FRequest
from requests import Request as RRequest
from uvicorn.config import LOGGING_CONFIG

from app.core.common.messages import UNEXPECTED_ERROR


class ApplicationLogger:
    """Configure and customize application logging"""

    __COLOR = {2: "\033[32m", 3: "\033[33m", 4: "\033[31m", 5: "\033[31m"}
    __UVICORN_FMT = "%(asctime)s %(levelprefix)s %(message)s"
    __UVICORN_LOGGER = "uvicorn.access"
    __FMT = "%(asctime)s %(message)s"
    __DATEFMT = "%d-%m-%Y %H:%M:%S"
    __NAME = "scopussurveyapi"
    __TABLE = str.maketrans(
        {
            "{": "\033[33m{\033[m",
            "}": "\033[33m}\033[m",
            "[": "\033[33m[\033[m",
            "]": "\033[33m]\033[m",
            ":": "\033[33m:\033[m",
            ",": "\033[33m,\033[m",
        }
    )
    __FOLDER = ".logs"

    class CleanFormatter(Formatter):
        __ANSI_ESCAPE_PATTERN = regex_compile(r"\x1b\[[3|9][0-7]m|\x1b\[m")

        def format(self, record) -> str:
            message = super().format(record)
            return self.__ANSI_ESCAPE_PATTERN.sub("", message)

    class EndpointFilter(Filter):
        def filter(self, record: LogRecord) -> bool:
            return record.getMessage().find("/") == -1

    class LiveReloadFilter(Filter):
        __LIVERELOAD_ROUTE = "/livereload"

        def filter(self, record: LogRecord) -> bool:
            return record.getMessage().find(self.__LIVERELOAD_ROUTE) == -1

    def __init__(
        self, debug: bool, logging_file: bool, host: str, port: int
    ) -> None:
        """Configure and customize application logging"""
        self.__logger = getLogger(self.__NAME)
        self.__logger.addFilter(self.LiveReloadFilter())
        self.__debug, self.__host, self.__port = debug, host, port

        getLogger(self.__UVICORN_LOGGER).addFilter(self.EndpointFilter())
        formater = {"fmt": self.__UVICORN_FMT, "datefmt": self.__DATEFMT}
        LOGGING_CONFIG["formatters"]["default"].update(formater)

        stream_formatter = Formatter(self.__FMT, self.__DATEFMT)
        self.__stream_handler = StreamHandler()
        self.__stream_handler.setFormatter(stream_formatter)
        self.__logger.addHandler(self.__stream_handler)

        if logging_file:
            now = datetime.now().strftime(self.__DATEFMT.replace(" ", "_"))
            filename = f"{self.__FOLDER}/{now}_app.log"

            if not exists(self.__FOLDER):
                mkdir(self.__FOLDER)

            file_formatter = self.CleanFormatter(self.__FMT, self.__DATEFMT)
            file_handler = FileHandler(filename)
            file_handler.setFormatter(file_formatter)
            self.__logger.addHandler(file_handler)

    @property
    def logger(self) -> list[Logger]:
        return [self.__logger]

    def info(self, message: str) -> None:
        self.__logger.setLevel(INFO)
        self.__logger.info(self.__message("32mINFO", message))

    def error(self, message: str, prefix: bool = None) -> None:
        if prefix:
            message = UNEXPECTED_ERROR.format(message)

        self.__logger.setLevel(ERROR)
        self.__logger.error(self.__message("91mERROR", message))

    def debug(self, data: dict) -> None:
        if self.__debug:
            json = f"JSON: \033[m{dumps(data).translate(self.__TABLE)}"
            self.__logger.setLevel(DEBUG)
            self.__logger.debug(self.__message("95mDEBUG", json))

    def exception(self, exception: Exception) -> None:
        message = UNEXPECTED_ERROR.format(repr(exception))
        exc_info = exception.__traceback__ is not None

        if exception.__traceback__:
            path = exception.__traceback__.tb_frame.f_code.co_filename
            line = exception.__traceback__.tb_lineno
            message = f"{message}\nFrom: {path}, line {line}"

        message = self.__message("91mEXCEPTION", message)
        self.__logger.setLevel(ERROR)
        self.__logger.exception(message, exc_info=exc_info)

    def trace(self, request: FRequest, code: int, time: float) -> None:
        message = self.__format(request, code, time)

        self.__logger.setLevel(INFO)
        self.__logger.info(self.__message("94mTRACE", message))

    def request(
        self, scopus: bool, request: RRequest, code: int, time: float
    ) -> None:
        prefix = "SEARCH" if scopus else "ABSTRACT"
        message = self.__format(request, code, time)

        self.__logger.setLevel(INFO)
        self.__logger.info(self.__message(f"96m{prefix}", message))

    def __format(
        self, request: FRequest | RRequest, code: int, time: float
    ) -> str:
        if not hasattr(request, "client"):
            setattr(request, "client", None)

        host = request.client.host if request.client else self.__host
        port = request.client.port if request.client else self.__port

        client = f"[\033[36m{host}\033[m:\033[36m{port}\033[m]"
        color = self.__COLOR[(code // 100)]

        method = f"{color}{request.method}\033[m"
        url = f"\033[37;1m{request.url}\033[m"

        status = f"{color}{code} {HTTPStatus(code).phrase}"
        process_time = f"\033[m{time:.2f}s"

        return f"\033[m{client} {method} {url} {status} {process_time}"

    def __message(self, prefix: str, message: str) -> str:
        return f"\033[{prefix}\033[m:".ljust(17) + f" \033[33m{message}\033[m"
