from asyncio import CancelledError, Semaphore
from asyncio import TimeoutError as AsyncTimeoutError
from asyncio import sleep
from http import HTTPStatus
from json import JSONDecodeError
from time import perf_counter

from aiohttp import (
    ClientConnectionError,
    ClientPayloadError,
    ClientSession,
    ClientTimeout,
    ContentTypeError,
    TCPConnector,
)
from aiohttp_retry import JitterRetry, RetryClient
from aiolimiter import AsyncLimiter

from src.core.common.error_messages import (
    CONNECTION_ERROR,
    CONNECTION_TIMEOUT,
    INVALID_JSON_ERROR,
    REQUEST_EXCEPTION,
)
from src.core.common.types import Json, ResponseBundle
from src.core.config.config import LOG
from src.core.config.scopus import SCOPUS_HEADERS
from src.core.domain.http_exceptions import (
    BadGateway,
    GatewayTimeout,
    HTTPError,
    ScopusAPIError,
)

# Scopus API Rate Limit:
# 8 of the max 9 requests per second, as leeway
# https://dev.elsevier.com/api_key_settings.html


class HTTPClient:
    """Make HTTP requests with throttling and retry mechanisms"""

    __ATTEMPTS = 3
    __RATE_PERIOD = 1.0
    __RATE_REQUESTS = 8.0
    __BACKOFF_FACTOR = 2
    __START_TIMEOUT = 0.5
    __MAX_TIMEOUT = 15.0
    __MAX_CONCURRENT_REQUESTS = 10
    __TIMEOUT = ClientTimeout(total=15.0)
    __JSON_ERROR = JSONDecodeError("Expecting value", "Scopus JSON", 0)
    __RETRYABLE_STATUS_CODES = {
        HTTPStatus.TOO_MANY_REQUESTS.value,
        HTTPStatus.INTERNAL_SERVER_ERROR.value,
        HTTPStatus.BAD_GATEWAY.value,
        HTTPStatus.SERVICE_UNAVAILABLE.value,
        HTTPStatus.GATEWAY_TIMEOUT.value,
    }
    __RETRYABLE_EXCEPTIONS = (
        AsyncTimeoutError,
        ClientConnectionError,
        ClientPayloadError,
    )
    __RETRY_OPTIONS = JitterRetry(
        attempts=__ATTEMPTS,
        start_timeout=__START_TIMEOUT,
        max_timeout=__MAX_TIMEOUT,
        factor=__BACKOFF_FACTOR,
        statuses=__RETRYABLE_STATUS_CODES,
        exceptions=__RETRYABLE_EXCEPTIONS,
    )

    def __init__(self) -> None:
        """Make HTTP requests with throttling and retry mechanisms"""
        self.__rate_limiter = AsyncLimiter(
            max_rate=self.__RATE_REQUESTS, time_period=self.__RATE_PERIOD
        )
        self.__semaphore = Semaphore(self.__MAX_CONCURRENT_REQUESTS)
        connector = TCPConnector(limit=self.__MAX_CONCURRENT_REQUESTS)
        self.__session = ClientSession(
            connector=connector,
            headers=SCOPUS_HEADERS,
            timeout=self.__TIMEOUT,
        )
        self.__retry_client = RetryClient(
            client_session=self.__session,
            retry_options=self.__RETRY_OPTIONS,
        )

    async def request(self, url: str) -> ResponseBundle:
        async with self.__rate_limiter, self.__semaphore:
            try:
                start_time = perf_counter()
                response = await self.__retry_client.get(
                    url, raise_for_status=False
                )
                process_time = perf_counter() - start_time

                LOG.api_call(url, response.status, process_time)

            except CancelledError as exc:
                raise exc

            except AsyncTimeoutError as exc:
                raise GatewayTimeout(CONNECTION_TIMEOUT, exc) from exc

            except ClientConnectionError as exc:
                raise BadGateway(CONNECTION_ERROR, exc) from exc

            except Exception as exc:
                raise BadGateway(REQUEST_EXCEPTION, exc) from exc

            try:
                data: Json | None = await response.json()
                if data is None:
                    raise self.__JSON_ERROR

            except (ContentTypeError, JSONDecodeError) as exc:
                raise ScopusAPIError(
                    HTTPStatus.BAD_GATEWAY,
                    HTTPError.get_error_details(exc)[0],
                    INVALID_JSON_ERROR,
                ) from exc

            return ResponseBundle(response.status, response.headers, data)

    async def close(self) -> None:
        await sleep(0)
        await self.__retry_client.close()
        await self.__session.close()
