import asyncio
import random
import time
from http import HTTPStatus
from json import JSONDecodeError

import aiohttp
import aiohttp_retry as aioretry
import aiolimiter

from src.core.common.types import Json, ResponseBundle
from src.core.config.scopus import RATE_LIMIT_ERROR_CODE, SCOPUS_HEADERS
from src.core.data.enums import ExcMsg
from src.core.domain.http_exceptions import (
    BadGateway,
    BadGatewayContent,
    GatewayTimeout,
)
from src.utils import logger


# Scopus API Rate Limit: 9 requests per second
# https://dev.elsevier.com/api_key_settings.html


class HTTPClient:  # pylint: disable=R0902
    """Make async HTTP requests with throttling and retry mechanisms

    **Note:** This client must be initialized within an async **event loop**
    """

    _JSON_ERROR = JSONDecodeError("Expecting value", "Scopus JSON", 0)
    _TIMEOUT = aiohttp.ClientTimeout(total=8.0)
    _RETRYABLE_STATUS_CODES = {
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
    _BATCH = 50

    def __init__(self) -> None:
        """Make async HTTP requests with throttling and retry mechanisms"""
        # Scopus standard rate limit with leeway (8req/s)
        self._limiter = aiolimiter.AsyncLimiter(max_rate=8.0, time_period=1.0)
        self._semaphore = asyncio.Semaphore(5)
        self._session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(),
            headers=SCOPUS_HEADERS,
            timeout=self._TIMEOUT,
        )
        self._retry_options = aioretry.JitterRetry(
            attempts=3,
            start_timeout=1.5,
            max_timeout=8.0,
            factor=2.0,
            statuses=self._RETRYABLE_STATUS_CODES,
            exceptions=self._RETRYABLE_EXCEPTIONS,
        )
        self._client = aioretry.RetryClient(
            client_session=self._session,
            retry_options=self._retry_options,
        )
        self._rate_limit_holder = asyncio.Event()
        self._rate_limit_holder.set()  # Procced
        self._request_count = 0
        self._lock = asyncio.Lock()

    def _rate_limit_exceeded(self, res: ResponseBundle) -> bool:
        if res.code == HTTPStatus.TOO_MANY_REQUESTS:
            error_res: Json | None = res.data.get("error-response")
            logger.debug({"scopus-error-response": error_res})

            if error_res and error_res.get("error-code"):
                return error_res["error-code"] == RATE_LIMIT_ERROR_CODE

        return False

    async def _track_batch(self):
        # Ensures execution of only one task at a time
        async with self._lock:
            self._request_count += 1
            should_sleep = self._request_count >= self._BATCH

            if should_sleep:
                self._request_count = 0
                self._rate_limit_holder.clear()  # Block

        # CRITICAL: The sleep execution MUST happen outside the lock context
        # Prevent task sleep from holding the lock for all other tasks,
        # causing massive lock contention/deadlocks for concurrency
        if should_sleep:
            await asyncio.sleep(1.5)
            self._rate_limit_holder.set()  # Proceed

    async def api_call(self, url: str) -> ResponseBundle:
        attempt = 1

        while True:
            await self._rate_limit_holder.wait()
            await asyncio.sleep(random.uniform(0.01, 0.1))
            await self._track_batch()

            res = await self._request(url)

            if not self._rate_limit_exceeded(res):
                return res

            if attempt >= 5:
                logger.error("Exhausted rate limit request retries")
                return res

            logger.error(f"HTTP 249 Rate Limit Exceeded ({attempt})")
            attempt += 1

            if self._rate_limit_holder.is_set():

                self._rate_limit_holder.clear()  # Block
                await asyncio.sleep(2)
                self._rate_limit_holder.set()  # Proceed

    async def _request(self, url: str) -> ResponseBundle:
        async with self._semaphore, self._limiter:
            await asyncio.sleep(random.uniform(0.01, 0.1))

            try:
                start_time = time.perf_counter()
                res = await self._client.get(url, raise_for_status=False)
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
        await self._client.close()
        await self._session.close()
