import asyncio
import bisect
import time
from http import HTTPStatus
from json import JSONDecodeError

import aiohttp
import aiohttp_retry as aioretry
import aiolimiter

from src.core.common.types import Json, RateStrategy, ResponseBundle
from src.core.config.scopus import SCOPUS_HEADERS
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import (
    BadGateway,
    BadGatewayContent,
    GatewayTimeout,
)
from src.utils import logger


# Scopus API Rate Limit: 9 requests per second
# https://dev.elsevier.com/api_key_settings.html


class HTTPClient:
    """Make async HTTP requests with throttling and retry mechanisms

    **Note:** This client must be initialized within an async **event loop**
    """

    _LEEWAY = 10
    _ATTEMPTS = 3
    _RATE_PERIOD = 1.0
    _BASE_STRATEGY = 100
    _START_TIMEOUT = 0.5
    _MAX_TIMEOUT = 15.0
    _TIMEOUT = aiohttp.ClientTimeout(total=15.0)
    _JSON_ERROR = JSONDecodeError("Expecting value", "Scopus JSON", 0)
    # Strategy:
    # - Rate (req/sec)
    # - Backoff factor
    # - Additional sleep (sec)
    # - Concurrent requests
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
        asyncio.TimeoutError,
        aiohttp.ClientConnectionError,
        aiohttp.ClientPayloadError,
    )
    _KEYS = sorted(_STRATEGIES.keys())

    def __init__(self) -> None:
        """Make async HTTP requests with throttling and retry mechanisms"""
        self._strategy: RateStrategy = self._STRATEGIES[self._BASE_STRATEGY]
        self._last_request_time: int = 0
        self._rate_limiter: aiolimiter.AsyncLimiter = None
        self._semaphore: asyncio.Semaphore = None
        self._session: aiohttp.ClientSession = None
        self._retry_options: aioretry.JitterRetry = None
        self._retry_client: aioretry.RetryClient = None
        self._mount()

    def _mount(self) -> None:
        self._rate_limiter = aiolimiter.AsyncLimiter(
            max_rate=self._strategy.rate, time_period=self._RATE_PERIOD
        )
        self._semaphore = asyncio.Semaphore(self._strategy.concurrent)
        connector = aiohttp.TCPConnector(limit=self._strategy.concurrent)

        self._session = aiohttp.ClientSession(
            connector=connector,
            headers=SCOPUS_HEADERS,
            timeout=self._TIMEOUT,
        )
        self._retry_options = aioretry.JitterRetry(
            attempts=self._ATTEMPTS,
            start_timeout=self._START_TIMEOUT,
            max_timeout=self._MAX_TIMEOUT,
            factor=self._strategy.backoff,
            statuses=self._RETRYABLE_STATUS_CODES,
            exceptions=self._RETRYABLE_EXCEPTIONS,
        )
        self._retry_client = aioretry.RetryClient(
            client_session=self._session,
            retry_options=self._retry_options,
        )
        logger.strategy(self._strategy)

    async def update_strategy(self, total_requests: int) -> None:
        if (total_requests - self._LEEWAY) <= self._BASE_STRATEGY:
            return None

        index = bisect.bisect_left(self._KEYS, (total_requests - self._LEEWAY))
        key = self._KEYS[index] if index < len(self._KEYS) else self._KEYS[-1]

        if self._STRATEGIES[key] != self._strategy:
            await self.close()
            self._strategy = self._STRATEGIES[key]
            self._mount()

        return None

    async def _additional_sleep(self) -> None:
        current_time = asyncio.get_event_loop().time()
        elapsed = current_time - self._last_request_time

        if elapsed < self._strategy.sleep:
            await asyncio.sleep(self._strategy.sleep - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def request(self, url: str) -> ResponseBundle:
        res = await self._send(url)

        if (
            res.code == HTTPStatus.TOO_MANY_REQUESTS
            and res.headers.get("X-RateLimit-Remaining") == "0"
        ):
            await asyncio.sleep(2)  # Wait 2 secs
            res = await self._send(url)

        return res

    async def _send(self, url: str) -> ResponseBundle:
        async with self._semaphore, self._rate_limiter:

            if self._strategy.sleep > 0:
                await self._additional_sleep()

            try:
                start_time = time.perf_counter()
                res = await self._retry_client.get(url, raise_for_status=False)
                process_time = time.perf_counter() - start_time

                logger.api_call(url, res.status, process_time)

            except asyncio.CancelledError as exc:
                raise exc

            except asyncio.TimeoutError as exc:
                raise GatewayTimeout(ExcMsg.CONNECTION_TIMEOUT, exc) from exc

            except aiohttp.ClientConnectionError as exc:
                raise BadGateway(ExcMsg.CONNECTION_ERROR, exc) from exc

            except Exception as exc:
                raise BadGateway(ExcMsg.REQUEST_EXCEPTION, exc) from exc

            try:
                data: Json | None = await res.json()
                if data is None:
                    raise self._JSON_ERROR

            except (aiohttp.ContentTypeError, JSONDecodeError) as exc:
                body = await res.text()
                raise BadGatewayContent(
                    ExcMsg.INVALID_JSON_ERROR, exc, body
                ) from exc

            return ResponseBundle(res.status, res.headers, data)

    async def close(self) -> None:
        await asyncio.sleep(0)
        await self._retry_client.close()
        await self._session.close()
