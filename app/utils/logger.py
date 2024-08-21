from datetime import datetime
from enum import Enum
from http import HTTPStatus
from json import dumps
from logging import (
    DEBUG,
    ERROR,
    INFO,
    FileHandler,
    Filter,
    Formatter,
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


class Logger:
    """Configure and customize application registration"""

    __FMT = "%(asctime)s %(message)s"
    __DATEFMT = "%d-%m-%Y %H:%M:%S"
    __UVICORN_FMT = "%(asctime)s %(levelprefix)s %(message)s"
    __UVICORN_LOGGER = "uvicorn.access"
    __POINT = "\033[95m\u2022\033[m"
    __FOLDER = ".logs"
    __TABLE = str.maketrans(
        {
            "{": "\033[93m{\033[m",
            "}": "\033[93m}\033[m",
            "[": "\033[93m[\033[m",
            "]": "\033[93m]\033[m",
            ":": "\033[93m:\033[m",
            ",": "\033[93m,\033[m",
        }
    )

    class CleanFormatter(Formatter):
        ANSI_ESCAPE_PATTERN = regex_compile(r"\x1b\[[3|9][0-7]m|\x1b\[m")

        def format(self, record) -> str:
            message = super().format(record)
            return self.ANSI_ESCAPE_PATTERN.sub("", message)

    class EndpointFilter(Filter):
        def filter(self, record: LogRecord) -> bool:
            return record.getMessage().find("/") == -1

    class Method(Enum):
        GET = "\033[94mGET\033[m"
        POST = "\033[92mPOST\033[m"
        PUT = "\033[93mPUT\033[m"
        PATCH = "\033[96mPATCH\033[m"
        DELETE = "\033[91mDELETE\033[m"

    def __init__(self, debug: bool, logging_file: bool) -> None:
        """Configure and customize application registration"""
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
    def logger(self):
        return [self.__logger]

    def __get_status(self, status_code: int, time: float) -> tuple[str, str]:
        status_phrase = HTTPStatus(status_code).phrase
        process_time = f"\033[93m{time:.2f}ms\033[m"

        status_color = 32 if status_code == 200 else 31
        status = f"\033[{status_color}m{status_code} {status_phrase}"

        return process_time, status

    def __format(self, level: str, message: str) -> str:
        level = f"\033[93m[\033[{level}\033[93m]:\033[m"
        return f"{level: <27} \033[93m{message}\033[m"

    def info(self, message: str) -> None:
        self.__logger.setLevel(INFO)
        self.__logger.info(self.__format("92mINFO", message))

    def error(self, message: str, default: bool = None) -> None:
        default = True if default is None else default
        message = UNEXPECTED_ERROR.format(message) if default else message
        self.__logger.setLevel(ERROR)
        self.__logger.error(self.__format("91mERROR", message))

    def debug(self, data: dict) -> None:
        if self.__debug:
            args = (2, "\n") if len(dumps(data)) > 150 else (None, "")
            json = dumps(data, indent=args[0]).translate(self.__TABLE)
            json = f"JSON: \033[m{args[1]}{json}"
            self.__logger.setLevel(DEBUG)
            self.__logger.debug(self.__format("95mDEBUG", json))

    def exception(self, exception: Exception) -> None:
        message = UNEXPECTED_ERROR.format(repr(exception))
        exc_info = exception.__traceback__ is not None

        if exception.__traceback__:
            path = exception.__traceback__.tb_frame.f_code.co_filename
            line = exception.__traceback__.tb_lineno
            message = f"{message}\nFrom: {path}, line {line}"

        message = self.__format("91mEXCEPTION", message)
        self.__logger.setLevel(ERROR)
        self.__logger.exception(message, exc_info=exc_info)

    def trace(self, request: Request, status_code: int, time: float) -> None:
        host = request.client.host if request.client else "127.0.0.1"
        port = request.client.port if request.client else 8000

        method = f"{self.Method[request.method].value: <6}"
        client = f"{host}\033[93m:\033[m{port}"
        url = f"{self.__POINT} {client} {self.__POINT} {request.url}"

        time = (current_time() - time) * 1000
        process_time, status = self.__get_status(status_code, time)
        message = f"{method} {url} {self.__POINT} {status} {process_time}"

        self.__logger.setLevel(INFO)
        self.__logger.info(self.__format("94mTRACE", message))

    def request(
        self, scopus: bool, url: str, status_code: int, time: float
    ) -> None:
        prefix = "SCOPUS" if scopus else "ARTICLE"
        process_time, status = self.__get_status(status_code, time)

        url = f"{self.Method.GET.value: <6} {self.__POINT} {url}"
        message = f"{url} {self.__POINT} {status} {process_time}"

        self.__logger.setLevel(INFO)
        self.__logger.info(self.__format(f"96m{prefix}", message))
