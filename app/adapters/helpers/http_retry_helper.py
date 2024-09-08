from time import time

from cachecontrol import CacheControlAdapter
from requests import Request, Response, Session
from requests.exceptions import ConnectionError as ConnectError, Timeout
from urllib3.util import Retry

from app.core.common.messages import (
    CONNECTION_ERROR,
    CONNECTION_EXCEPTION,
    CONNECTION_TIMEOUT,
)
from app.core.common.types import Headers
from app.core.config.config import LOG
from app.core.domain.metaclasses import HTTPRetry
from app.framework.exceptions import BadGateway, GatewayTimeout


class HTTPRetryHelper(HTTPRetry):
    """Make HTTP requests with throttling and retry mechanisms"""

    __METHOD = "GET"
    __PREFIX = "https://"
    __RETRIES = 3
    __TIMEOUT = 15
    __SLEEP_FACTOR = 0.7
    __STATUS_LIST = {400, 401, 403, 404, 429, 500}
    __RETRY = Retry(
        total=__RETRIES,
        connect=__RETRIES,
        read=__RETRIES,
        status=__RETRIES,
        other=__RETRIES,
        allowed_methods={__METHOD},
        status_forcelist=__STATUS_LIST,
        backoff_factor=__SLEEP_FACTOR,
        raise_on_status=False,
    )

    def __init__(self, for_scopus: bool = None) -> None:
        """Make HTTP requests with throttling and retry mechanisms"""
        self.__adapter = CacheControlAdapter(max_retries=self.__RETRY)
        self.__for_scopus = True if for_scopus is None else for_scopus
        self.__headers: Headers = None
        self.__session: Session = None

    def mount_session(self, headers: Headers) -> None:
        self.__headers = headers
        self.__session = Session()
        self.__session.mount(self.__PREFIX, self.__adapter)

    def close(self) -> None:
        self.__adapter.close()
        self.__session.close()

    def request(self, url: str) -> Response:
        request = Request(self.__METHOD, url, self.__headers)
        prepared_request = self.__session.prepare_request(request)

        try:
            start_time = time()
            response = self.__session.send(
                prepared_request, timeout=self.__TIMEOUT
            )
            process_time = (time() - start_time) * 1000

            LOG.request(
                self.__for_scopus,
                url,
                response.status_code,
                process_time,
            )

        except Timeout as error:
            raise GatewayTimeout(CONNECTION_TIMEOUT) from error

        except ConnectError as error:
            raise BadGateway(CONNECTION_ERROR) from error

        except Exception as error:
            message = CONNECTION_EXCEPTION.format(repr(error))
            raise BadGateway(message) from error

        return response
