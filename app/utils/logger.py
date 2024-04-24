from datetime import datetime
from enum import Enum
from http import HTTPStatus
from logging import INFO, FileHandler, Formatter, StreamHandler, getLogger
from os import mkdir, path
from re import compile as regex_compile
from sys import exc_info

from fastapi import Request

from app.core.config import TOML


class Logger:
    __INSTANCE = None
    LOG_RULE = '%(asctime)s %(message)s'
    DATE_RULE = '%d-%m-%Y %H:%M:%S'
    POINT = '\033[95m\u2022\033[m'

    def __init__(self) -> None:
        self.__logger = getLogger(__name__)

    def __new__(cls):
        if cls.__INSTANCE is None:
            cls.__INSTANCE = super(Logger, cls).__new__(cls)
            cls.__INSTANCE.set_logger()
        return cls.__INSTANCE

    class CleanFormatter(Formatter):
        ANSI_ESCAPE_PATTERN = regex_compile(r'\x1b\[[3|9][0-7]m|\x1b\[m')

        def format(self, record) -> str:
            message = super().format(record)
            return self.ANSI_ESCAPE_PATTERN.sub('', message, 20)

    class Level(Enum):
        INFO = '\033[93m[\033[92mINFO\033[93m]:\033[m'
        ERROR = '\033[93m[\033[91mERROR\033[93m]:\033[m'
        EXCEPTION = '\033[93m[\033[91mEXCEPTION\033[93m]:\033[m'
        TRACE = '\033[93m[\033[95mTRACE\033[93m]:\033[m'
        SERVICE = '\033[93m[\033[95mSERVICE\033[93m]:\033[m'

    class Method(Enum):
        GET = '\033[94mGET\033[m'
        POST = '\033[92mPOST\033[m'
        PUT = '\033[93mPUT\033[m'
        PATCH = '\033[96mPATCH\033[m'
        DELETE = '\033[91mDELETE\033[m'

    def set_logger(self) -> None:
        self.__logger = getLogger(__name__)
        self.__logger.setLevel(INFO)

        stream_formatter = Formatter(self.LOG_RULE, self.DATE_RULE)
        stream_handler = StreamHandler()
        stream_handler.setFormatter(stream_formatter)
        self.__logger.addHandler(stream_handler)

        if TOML.logging_file:
            now = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
            filename = f'logs/{now}_app.log'

            if not path.exists('logs'):
                mkdir('logs')

            file_formatter = self.CleanFormatter(self.LOG_RULE, self.DATE_RULE)
            file_handler = FileHandler(filename)
            file_handler.setFormatter(file_formatter)
            self.__logger.addHandler(file_handler)

    def log(self, level: Level, message: str) -> None:
        log = f'{level.value: <24} \033[93m{message}\033[m'
        self.__logger.info(log)

    @classmethod
    def get_status(cls, status_code: int, time: float) -> tuple[str, str]:
        status_phrase = HTTPStatus(status_code).phrase
        process_time = f'\033[93m{time:.2f}ms\033[m'

        status_color = 32 if status_code == 200 else 31
        status = f'\033[{status_color}m{status_code} {status_phrase}'

        return process_time, status

    @classmethod
    def info(cls, message: str) -> None:
        Logger().log(cls.Level.INFO, message)

    @classmethod
    def error(cls, message: str) -> None:
        log = f'\033[93mArticle Preview Page: \033[91m{message}\033[m'
        Logger().log(cls.Level.ERROR, log)

    @classmethod
    def exception(cls, exception: Exception) -> None:
        exception_type, exception_value, exception_traceback = exc_info()
        exception_name = getattr(exception_type, '__name__', 'Exception')

        message = f'<{exception_name}({exception.args}): {exception_value}>'
        Logger().log(cls.Level.EXCEPTION, f'Unexpected Error {message}')

        if exception_traceback is not None:
            fname = path.split(exception_traceback.tb_frame.f_code.co_filename)
            message = (
                f'Unexpected Error {exception_type} {fname} '
                f'{exception_traceback.tb_lineno}'
            )
            Logger().log(cls.Level.EXCEPTION, message)

    @classmethod
    def trace(cls, request: Request, status_code: int, time: float) -> None:
        host = request.client.host if request.client else '127.0.0.1'
        port = request.client.port if request.client else '8000'

        method = f'{cls.Method[request.method].value: <6}'
        url = f'{cls.POINT} http://{host}:{port}{request.url}'

        process_time, status = cls.get_status(status_code, time)
        message = f'{method} {url} {cls.POINT} {status} {process_time}'

        Logger().log(cls.Level.TRACE, message)

    @classmethod
    def service(cls, url: str, status_code: int, time: float) -> None:
        process_time, status = cls.get_status(status_code, time)
        url = f'{cls.Method.GET.value: <6} {cls.POINT} {url}'
        message = f'{url} {cls.POINT} {status} {process_time}'

        Logger().log(cls.Level.SERVICE, message)
