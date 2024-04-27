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
from os import mkdir, path
from re import compile as regex_compile
from sys import exc_info

from fastapi import Request
from uvicorn.config import LOGGING_CONFIG


class Logging:
    FMT = '%(asctime)s %(message)s'
    DATEFMT = '%d-%m-%Y %H:%M:%S'
    UVICORN_FMT = '%(asctime)s %(levelprefix)s %(message)s'
    UVICORN_LOGGER = 'uvicorn.access'
    POINT = '\033[95m\u2022\033[m'
    FOLDER = 'logs'
    BAR_SIZE = 30
    TABLE = str.maketrans(
        {
            '{': '\033[93m{\033[m',
            '}': '\033[93m}\033[m',
            '[': '\033[93m[\033[m',
            ']': '\033[93m]\033[m',
            ':': '\033[93m:\033[m',
            ',': '\033[93m,\033[m',
        }
    )

    class CleanFormatter(Formatter):
        ANSI_ESCAPE_PATTERN = regex_compile(r'\x1b\[[3|9][0-7]m|\x1b\[m')

        def format(self, record) -> str:
            message = super().format(record)
            return self.ANSI_ESCAPE_PATTERN.sub('', message)

    class EndpointFilter(Filter):
        def filter(self, record: LogRecord) -> bool:
            return record.getMessage().find('/') == -1

    class Method(Enum):
        GET = '\033[94mGET\033[m'
        POST = '\033[92mPOST\033[m'
        PUT = '\033[93mPUT\033[m'
        PATCH = '\033[96mPATCH\033[m'
        DELETE = '\033[91mDELETE\033[m'

    def __init__(self, debug: bool, logging_file: bool) -> None:
        self.__debug = debug
        self.__logger = getLogger(__name__)
        self.__disable_uvicorn_logging()

        stream_formatter = Formatter(self.FMT, self.DATEFMT)
        stream_handler = StreamHandler()
        stream_handler.setFormatter(stream_formatter)
        self.__logger.addHandler(stream_handler)

        if logging_file:
            self.__enable_logging_file()

    def __enable_logging_file(self):
        now = datetime.now().strftime(self.DATEFMT.replace(' ', '_'))
        filename = f'{self.FOLDER}/{now}_app.log'

        if not path.exists(self.FOLDER):
            mkdir(self.FOLDER)

        file_formatter = self.CleanFormatter(self.FMT, self.DATEFMT)
        file_handler = FileHandler(filename)
        file_handler.setFormatter(file_formatter)
        self.__logger.addHandler(file_handler)

    def __disable_uvicorn_logging(self):
        getLogger(self.UVICORN_LOGGER).addFilter(self.EndpointFilter())
        formater = {'fmt': self.UVICORN_FMT, 'datefmt': self.DATEFMT}
        LOGGING_CONFIG['formatters']['default'].update(formater)

    def __get_status(self, status_code: int, time: float) -> tuple[str, str]:
        status_phrase = HTTPStatus(status_code).phrase
        process_time = f'\033[93m{time:.2f}ms\033[m'

        status_color = 32 if status_code == 200 else 31
        status = f'\033[{status_color}m{status_code} {status_phrase}'

        return process_time, status

    def __format(self, level: str, message: str) -> str:
        level = f'\033[93m[\033[{level}\033[93m]:\033[m'
        return f'{level: <27} \033[93m{message}\033[m'

    def __json(self, data: dict):
        args = (2, '\n') if len(dumps(data)) > 150 else (None, '')
        json = dumps(data, indent=args[0]).translate(self.TABLE)
        return f'JSON: \033[m{args[1]}{json}'

    def info(self, message: str) -> None:
        self.__logger.setLevel(INFO)
        self.__logger.info(self.__format('92mINFO', message))

    def error(self, message: str) -> None:
        message = f'\033[93mArticle Preview Page: \033[91m{message}\033[m'
        self.__logger.setLevel(ERROR)
        self.__logger.error(self.__format('91mERROR', message))

    def debug(self, data: dict) -> None:
        if self.__debug:
            self.__logger.setLevel(DEBUG)
            self.__logger.debug(self.__format('95mDEBUG', self.__json(data)))

    def exception(self, exception: Exception) -> None:
        exception_type, exception_value, exception_traceback = exc_info()
        exception_name = getattr(exception_type, '__name__', 'Exception')

        message = f'<{exception_name}({exception.args}): {exception_value}>'
        self.__logger.setLevel(ERROR)

        message = self.__format('91mEXCEPTION', f'Unexpected Error {message}')
        self.__logger.exception(message)

        if exception_traceback is not None:
            fname = path.split(exception_traceback.tb_frame.f_code.co_filename)
            message = (
                f'Unexpected Error {exception_type} {fname} '
                f'{exception_traceback.tb_lineno}'
            )
            message = self.__format('91mEXCEPTION', message)
            self.__logger.exception(message, exc_info=True)

    def trace(self, request: Request, status_code: int, time: float) -> None:
        host = request.client.host if request.client else '127.0.0.1'
        port = request.client.port if request.client else 8000

        method = f'{self.Method[request.method].value: <6}'
        client = f'{host}\033[93m:\033[m{port}'
        url = f'{self.POINT} {client} {self.POINT} {request.url}'

        process_time, status = self.__get_status(status_code, time)
        message = f'{method} {url} {self.POINT} {status} {process_time}'

        self.__logger.setLevel(INFO)
        self.__logger.info(self.__format('94mTRACE', message))

    def request(
        self, check_status: bool, url: str, status_code: int, time: float
    ) -> None:
        prefix = 'SCOPUS' if not check_status else 'SCRAPING'
        process_time, status = self.__get_status(status_code, time)

        url = f'{self.Method.GET.value: <6} {self.POINT} {url}'
        message = f'{url} {self.POINT} {status} {process_time}'

        self.__logger.setLevel(INFO)
        self.__logger.info(self.__format(f'96m{prefix}', message))

    def progress(self, index: int, total: int) -> None:
        part = int(index / (total / self.BAR_SIZE))
        percentage = f'{((index) / total) * 100:.2f}'

        progress_bar = '\x1b[92m\u25AC\x1b[m' * part
        progress_bar += '\x1b[91m\u25AC\x1b[m' * (self.BAR_SIZE - part)

        message = (
            f"\u25FE{str(index).rjust(len(str(total)), ' ')}/{total}"
            f' {progress_bar}\x1b[93m {percentage:>6}%\x1b[m'
        )

        self.__logger.setLevel(INFO)
        self.__logger.info(self.__format('92mINFO', message))
