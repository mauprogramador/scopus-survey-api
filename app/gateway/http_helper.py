from time import time

from requests import Request, Response, Session
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as ConnectError
from requests.exceptions import Timeout

from app.core.interfaces import Helper
from app.exceptions.http_exceptions import FailedDependency
from app.utils.logger import Logger


class HttpHelper(Helper):
    @staticmethod
    def make_request(url: str, headers: dict) -> Response:
        adapter = HTTPAdapter(max_retries=3)
        request = Request('GET', url, headers)

        with Session() as session:
            session.mount('https://', adapter)
            start_time = time()

            try:
                response = session.send(request.prepare(), timeout=15)

            except Timeout as exc:
                raise FailedDependency('Request Connection Timeout') from exc

            except ConnectError as exc:
                raise FailedDependency('Connection Error in Request') from exc

            except Exception as exc:
                message = f'Unexpected Error from Request: {exc.args[0]}'
                raise FailedDependency(message) from exc

        process_time = (time() - start_time) * 1000

        Logger.service(url, response, process_time)

        return response
