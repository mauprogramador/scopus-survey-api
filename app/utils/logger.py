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
from time import time as current_time

from fastapi import Request
from uvicorn.config import LOGGING_CONFIG

from app.core.common.messages import UNEXPECTED_ERROR


class AppLogger:
    """Configure and customize application logging"""

    __UVICORN_FMT = "%(asctime)s %(levelprefix)s %(message)s"
    __UVICORN_LOGGER = "uvicorn.access"
    __FMT = "%(asctime)s %(message)s"
    __POINT = "\033[35m\u2022\033[m"
    __DATEFMT = "%d-%m-%Y %H:%M:%S"
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
        ANSI_ESCAPE_PATTERN = regex_compile(r"\x1b\[[3|9][0-7]m|\x1b\[m")

        def format(self, record) -> str:
            message = super().format(record)
            return self.ANSI_ESCAPE_PATTERN.sub("", message)

    class EndpointFilter(Filter):
        def filter(self, record: LogRecord) -> bool:
            return record.getMessage().find("/") == -1

    def __init__(self, debug: bool, logging_file: bool) -> None:
        """Configure and customize application logging"""
        self.__debug = debug
        self.__logger = getLogger(__name__)

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

    def trace(self, request: Request, code: int, time: float) -> None:
        host = request.client.host if request.client else "127.0.0.1"
        port = request.client.port if request.client else 8000

        time = (current_time() - time) * 1000
        text = f"{host}:{port} {self.__POINT} {request.url}"
        message = self.__format(code, time, request.method, text)

        self.__logger.setLevel(INFO)
        self.__logger.info(self.__message("94mTRACE", message))

    def request(self, scopus: bool, url: str, code: int, time: float) -> None:
        prefix = "SEARCH" if scopus else "ABSTRACT"
        message = self.__format(code, time, "GET", url)

        self.__logger.setLevel(INFO)
        self.__logger.info(self.__message(f"96m{prefix}", message))

    def __message(self, prefix: str, message: str) -> str:
        return f"\033[{prefix}\033[m:".ljust(17) + f" \033[33m{message}\033[m"

    def __format(self, code: int, time: float, method: str, text: str) -> str:
        status_phrase = HTTPStatus(code).phrase
        color = "\033[32m" if code == 200 else "\033[31m"

        method = f"{color}{method}\033[m".ljust(6)
        status = f"{color}{code} {status_phrase} \033[33m{time:.2f}ms\033[m"

        return f"{method} {self.__POINT} {text} {self.__POINT} {status}"
