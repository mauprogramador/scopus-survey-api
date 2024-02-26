from http import HTTPStatus
from os.path import split
from sys import exc_info

from fastapi import Request, Response
from requests import Response as RequestsResponse


class Logger:
    METHOD = {
        'GET': '\033[94mGET\033[m',
        'POST': '\033[92mPOST\033[m',
        'PUT': '\033[93mPUT\033[m',
        'PATCH': '\033[96mPATCH\033[m',
        'DELETE': '\033[91mDELETE\033[m',
    }

    @classmethod
    def log(cls, prefix: str, message: str) -> None:
        log_type = f'\033[93m[{prefix}\033[93m]:'
        print(f'{log_type: <24}\033[m {message}')

    @classmethod
    def info(cls, message: str) -> None:
        cls.log('\033[92mINFO', message)

    @classmethod
    def error(cls, message: str) -> None:
        cls.log('\033[91mERROR', message)

    @classmethod
    def exception(cls, exception: Exception) -> None:
        exception_type, exception_value, exception_traceback = exc_info()
        exception_name = getattr(exception_type, '__name__', 'Exception')

        prefix = '\033[91mEXCEPTION'
        message = f'<{exception_name}({exception.args}): {exception_value}>'
        cls.log(prefix, f'Unexpected Error {message}')

        if exception_traceback is not None:
            fname = split(exception_traceback.tb_frame.f_code.co_filename)
            message = (
                f'Unexpected Error {exception_type} {fname} '
                f'{exception_traceback.tb_lineno}'
            )
            cls.log(prefix, message)

    @classmethod
    def trace(
        cls, request: Request, response: Response, process_time: float
    ) -> None:
        status_code = response.status_code

        host = request.client.host if request.client else '127.0.0.1'
        port = request.client.port if request.client else '8000'

        status_phrase = HTTPStatus(status_code).phrase
        process_time = f'\033[93m{process_time:.2f}ms\033[m'

        point = '\033[95m\u2022\033[m'
        status_color = 32 if status_code in (200, 201) else 31

        method = f'{cls.METHOD[request.method]: <6}'
        url = f'{point} http://{host}:{port}{request.url}'

        status = f'\033[{status_color}m{status_code} {status_phrase}'
        message = f'{method} {url} {point} {status} {process_time}'

        cls.log('\033[95mTRACE', message)

    @classmethod
    def service(
        cls, url: str, response: RequestsResponse, process_time: float
    ) -> None:
        status_code = response.status_code
        status_phrase = HTTPStatus(status_code).phrase
        process_time = f'\033[93m{process_time:.2f}ms\033[m'

        point = '\033[95m\u2022\033[m'
        status_color = 32 if status_code in (200, 201) else 31
        url = f"{cls.METHOD['GET']: <6} {point} {url}"

        status = f'\033[{status_color}m{status_code} {status_phrase}'
        message = f'{url} {point} {status} {process_time}'

        cls.log('\033[95mSERVICE', message)
