from http import HTTPStatus
from time import sleep, time

from requests import Request, Response, Session
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as ConnectError
from requests.exceptions import Timeout

from app.core.interfaces import Helper
from app.framework.exceptions.http_exceptions import FailedDependency
from app.utils.logger import Logger


class HttpHelper(Helper):
    METHOD = 'GET'
    PREFIX = 'https://'

    def __init__(self) -> None:
        self.__request = Request()
        self.__check_status = True
        self.__start_time = 0.0
        self.__process_time = 0.0

    def send_request(self, session: Session) -> Response:
        try:
            response = session.send(self.__request.prepare(), timeout=15)

            if self.__check_status and response.status_code != 200:
                raise FailedDependency(
                    f'Unexpected status error {response.status_code} '
                    f'{HTTPStatus(response.status_code).phrase}'
                )

            return response

        except FailedDependency as error:
            raise error

        except Timeout as error:
            raise FailedDependency('Request Connection Timeout') from error

        except ConnectError as error:
            raise FailedDependency('Connection Error in Request') from error

        except Exception as error:
            message = f'Unexpected Error from Request: {error.args[0]}'
            raise FailedDependency(message) from error

    def make_request(
        self, url: str, headers: dict, check_status: bool = None
    ) -> Response:

        adapter = HTTPAdapter(max_retries=3)
        self.__request = Request(self.METHOD, url, headers)

        if check_status is not None:
            self.__check_status = check_status

        with Session() as session:
            session.mount(self.PREFIX, adapter)

            for count in range(3):
                try:
                    self.__start_time = time()
                    response = self.send_request(session)
                    self.__process_time = (time() - self.__start_time) * 1000

                    Logger.service(
                        url, response.status_code, self.__process_time
                    )
                    break

                except FailedDependency as error:
                    if count >= 2:
                        raise error

                    process_time = (time() - self.__start_time) * 1000
                    Logger.service(url, error.status_code, process_time)

                    Logger.info('Retrying the request')
                    sleep(5)

        return response
