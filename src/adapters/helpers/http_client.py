from asyncio import CancelledError, Semaphore, get_event_loop
from asyncio import TimeoutError as AsyncTimeoutError
from asyncio import sleep
from bisect import bisect_left
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
from src.core.common.types import Json, RateStrategy, ResponseBundle
from src.core.config.config import LOG
from src.core.config.scopus import SCOPUS_HEADERS
from src.core.domain.http_exceptions import (
    BadGateway,
    GatewayTimeout,
    HTTPError,
    ScopusAPIError,
)

# Scopus API Rate Limit: 9 requests per second
# https://dev.elsevier.com/api_key_settings.html


class HTTPClient:
    """Make HTTP requests with throttling and retry mechanisms"""

    _LEEWAY = 10
    _ATTEMPTS = 3
    _RATE_PERIOD = 1.0
    _BASE_STRATEGY = 100
    _START_TIMEOUT = 0.5
    _MAX_TIMEOUT = 15.0
    _TIMEOUT = ClientTimeout(total=15.0)
    _JSON_ERROR = JSONDecodeError("Expecting value", "Scopus JSON", 0)
    _STRATEGIES = {
        100: RateStrategy(8.0, 2.0, 0.0, 10),
        200: RateStrategy(7.5, 2.2, 0.0, 10),
        300: RateStrategy(7.0, 2.5, 0.05, 8),
        400: RateStrategy(6.5, 2.8, 0.1, 6),
        500: RateStrategy(6.0, 3.0, 0.15, 5),
        750: RateStrategy(5.5, 3.2, 0.2, 4),
        1000: RateStrategy(5.0, 3.5, 0.25, 3),
        1500: RateStrategy(4.5, 4.0, 0.3, 3),
        2000: RateStrategy(4.0, 4.5, 0.35, 2),
    }
    _RETRYABLE_STATUS_CODES = {
        HTTPStatus.TOO_MANY_REQUESTS.value,
        HTTPStatus.INTERNAL_SERVER_ERROR.value,
        HTTPStatus.BAD_GATEWAY.value,
        HTTPStatus.SERVICE_UNAVAILABLE.value,
        HTTPStatus.GATEWAY_TIMEOUT.value,
    }
    _RETRYABLE_EXCEPTIONS = (
        AsyncTimeoutError,
        ClientConnectionError,
        ClientPayloadError,
    )
    _KEYS = sorted(_STRATEGIES.keys())

    def __init__(self) -> None:
        """Make HTTP requests with throttling and retry mechanisms"""
        self._strategy: RateStrategy = self._STRATEGIES[self._BASE_STRATEGY]
        self._last_request_time: int = 0
        self._rate_limiter: AsyncLimiter = None
        self._semaphore: Semaphore = None
        self._session: ClientSession = None
        self._retry_options: JitterRetry = None
        self._retry_client: RetryClient = None
        self._mount()

    def _mount(self) -> None:
        self._rate_limiter = AsyncLimiter(
            max_rate=self._strategy.rate, time_period=self._RATE_PERIOD
        )
        self._semaphore = Semaphore(self._strategy.concurrent)
        connector = TCPConnector(limit=self._strategy.concurrent)

        self._session = ClientSession(
            connector=connector,
            headers=SCOPUS_HEADERS,
            timeout=self._TIMEOUT,
        )
        self._retry_options = JitterRetry(
            attempts=self._ATTEMPTS,
            start_timeout=self._START_TIMEOUT,
            max_timeout=self._MAX_TIMEOUT,
            factor=self._strategy.backoff,
            statuses=self._RETRYABLE_STATUS_CODES,
            exceptions=self._RETRYABLE_EXCEPTIONS,
        )
        self._retry_client = RetryClient(
            client_session=self._session,
            retry_options=self._retry_options,
        )
        LOG.strategy(self._strategy, self._RATE_PERIOD)

    async def update_strategy(self, total_requests: int) -> None:
        if (total_requests - self._LEEWAY) <= self._BASE_STRATEGY:
            return None

        index = bisect_left(self._KEYS, (total_requests - self._LEEWAY))
        key = self._KEYS[index] if index < len(self._KEYS) else self._KEYS[-1]

        if self._STRATEGIES[key] != self._strategy:
            self._strategy = self._STRATEGIES[key]
            await self.close()
            self._mount()

        return None

    async def _additional_sleep(self) -> None:
        current_time = get_event_loop().time()
        elapsed = current_time - self._last_request_time

        if elapsed < self._strategy.sleep:
            print(self._strategy.sleep - elapsed)
            await sleep(self._strategy.sleep - elapsed)
        self._last_request_time = get_event_loop().time()

    async def request(self, url: str) -> ResponseBundle:
        response = await self._send(url)

        if (
            response.code == HTTPStatus.TOO_MANY_REQUESTS
            and response.headers.get("X-RateLimit-Remaining") == "0"
        ):
            await sleep(2)  # Wait 2 secs
            response = await self._send(url)

        return response

    async def _send(self, url: str) -> ResponseBundle:
        async with self._semaphore, self._rate_limiter:

            if self._strategy.sleep > 0:
                await self._additional_sleep()

            try:
                start_time = perf_counter()
                response = await self._retry_client.get(
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
                    raise self._JSON_ERROR

            except (ContentTypeError, JSONDecodeError) as exc:
                raise ScopusAPIError(
                    HTTPStatus.BAD_GATEWAY,
                    HTTPError.get_error_details(exc)[0],
                    INVALID_JSON_ERROR,
                ) from exc

            return ResponseBundle(response.status, response.headers, data)

    async def close(self) -> None:
        await sleep(0)
        await self._retry_client.close()
        await self._session.close()
