from asyncio import CancelledError, Semaphore
from asyncio import TimeoutError as AsyncTimeoutError
from asyncio import sleep
from http import HTTPStatus
from time import perf_counter

from aiohttp import (
    ClientConnectionError,
    ClientError,
    ClientResponse,
    ClientSession,
    ClientTimeout,
)
from aiohttp_retry import JitterRetry, RetryClient
from aiolimiter import AsyncLimiter

from src.core.common.messages import (
    CANCELLED_ERROR,
    CLIENT_EXCEPTION,
    CONNECTION_ERROR,
    CONNECTION_TIMEOUT,
    REQUEST_EXCEPTION,
)
from src.core.config.config import LOG
from src.core.config.scopus import SCOPUS_HEADERS
from src.core.domain.http_exceptions import BadGateway, GatewayTimeout
from src.core.domain.interfaces import HTTPClientABC
from src.utils.logging import Prefix


class HTTPClient(HTTPClientABC):
    """Make HTTP requests with throttling and retry mechanisms"""

    __RETRIES = 4
    __RATE_PERIOD = 1.0
    __RATE_REQUESTS = 10.0
    __BACKOFF_FACTOR = 1.5
    __MAX_CONCURRENT_REQUESTS = 10
    __TIMEOUT = ClientTimeout(total=15.0)
    __RETRYABLE_STATUS_CODES = {
        HTTPStatus.BAD_REQUEST.value,
        HTTPStatus.UNAUTHORIZED.value,
        HTTPStatus.FORBIDDEN.value,
        HTTPStatus.NOT_FOUND.value,
        HTTPStatus.TOO_MANY_REQUESTS.value,
        HTTPStatus.INTERNAL_SERVER_ERROR.value,
    }
    __RETRYABLE_EXCEPTIONS = (
        AsyncTimeoutError,
        ClientError,
    )
    __RETRY_OPTIONS = JitterRetry(
        attempts=__RETRIES,
        factor=__BACKOFF_FACTOR,
        statuses=__RETRYABLE_STATUS_CODES,
        exceptions=__RETRYABLE_EXCEPTIONS,
    )

    def __init__(self, for_search: bool) -> None:
        """Make HTTP requests with throttling and retry mechanisms"""
        self.__log_prefix = Prefix.SEARCH if for_search else Prefix.ABSTRACT
        # 10 of the max 9 requests per second, as leeway
        # https://dev.elsevier.com/api_key_settings.html
        self.__rate_limiter = AsyncLimiter(
            max_rate=self.__RATE_REQUESTS, time_period=self.__RATE_PERIOD
        )
        self.__semaphore = Semaphore(self.__MAX_CONCURRENT_REQUESTS)
        self.__session = ClientSession(
            headers=SCOPUS_HEADERS, timeout=self.__TIMEOUT
        )
        self.__retry_client = RetryClient(
            client_session=self.__session,
            retry_options=self.__RETRY_OPTIONS,
        )

    async def request(self, url: str) -> ClientResponse:
        async with self.__rate_limiter, self.__semaphore:
            try:
                start_time = perf_counter()
                response = await self.__retry_client.get(
                    url, raise_for_status=False
                )
                process_time = perf_counter() - start_time

                LOG.trace(
                    self.__log_prefix,
                    LOG.build_request_obj(url),
                    response.status,
                    process_time,
                )

            except AsyncTimeoutError as exc:
                raise GatewayTimeout(CONNECTION_TIMEOUT, exc) from exc

            except CancelledError as exc:
                raise BadGateway(CANCELLED_ERROR, exc) from exc

            except ClientConnectionError as exc:
                raise BadGateway(CONNECTION_ERROR, exc) from exc

            except ClientError as exc:
                raise BadGateway(CLIENT_EXCEPTION, exc) from exc

            except Exception as exc:
                raise BadGateway(REQUEST_EXCEPTION, exc) from exc

            return response

    async def close(self) -> None:
        await self.__retry_client.close()
        await self.__session.close()
        await sleep(0)
