"""Shared, bounded and safe asynchronous HTTP client."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Mapping
from email.utils import parsedate_to_datetime
from time import time
from typing import Any

import httpx

from ..config import Settings
from .errors import (
    AuthenticationError,
    AuthorizationError,
    ExternalAPIError,
    RateLimitError,
)
from .security import validate_external_url

logger = logging.getLogger(__name__)


class HttpClient:
    """Reusable HTTP client with timeout, allow-list and bounded retry behavior.

    The client owns one ``httpx.AsyncClient`` and must be closed with ``aclose``
    when the service lifecycle ends. Only idempotent GET requests are retried.
    """

    def __init__(self, settings: Settings, *, allowed_hosts: set[str] | frozenset[str]) -> None:
        self._settings = settings
        self._allowed_hosts = allowed_hosts
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._settings.http_timeout_seconds),
                follow_redirects=False,
            )
        return self._client

    async def aclose(self) -> None:
        """Close the underlying connection pool."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str | int | float | None] | None = None,
        json: Any = None,
    ) -> httpx.Response:
        """Perform an allow-listed request and map failures to safe exceptions."""
        validate_external_url(url, self._allowed_hosts)
        normalized_method = method.upper()
        retries = self._settings.max_retries if normalized_method == "GET" else 0

        for attempt in range(retries + 1):
            try:
                response = await self._get_client().request(
                    normalized_method,
                    url,
                    headers=headers,
                    params=params,
                    json=json,
                )
            except httpx.TimeoutException as exc:
                if attempt < retries:
                    await asyncio.sleep(2**attempt)
                    continue
                raise ExternalAPIError("The external API request timed out.") from exc
            except httpx.RequestError as exc:
                if attempt < retries:
                    await asyncio.sleep(2**attempt)
                    continue
                raise ExternalAPIError("The external API request failed.") from exc

            if response.status_code == 429:
                retry_after = _retry_after_seconds(response.headers.get("retry-after"))
                if attempt < retries:
                    await asyncio.sleep(retry_after or 2**attempt)
                    continue
                raise RateLimitError("The external API rate limit was reached.", retry_after=retry_after)

            if response.status_code in {500, 502, 503, 504} and attempt < retries:
                await asyncio.sleep(2**attempt)
                continue

            _raise_for_status(response)
            return response

        raise ExternalAPIError("The external API request failed after retries.")



def _raise_for_status(response: httpx.Response) -> None:
    """Convert an HTTP response to a safe domain error without returning its body."""
    status = response.status_code
    if 200 <= status < 300:
        return
    logger.warning("External API returned HTTP status %s", status)
    if status == 401:
        raise AuthenticationError("The external API rejected the configured credentials.")
    if status == 403:
        raise AuthorizationError("The configured credentials lack the required permission.")
    if status == 404:
        raise ExternalAPIError("The requested external resource was not found.", status_code=status)
    raise ExternalAPIError("The external API returned an error.", status_code=status)


def _retry_after_seconds(value: str | None) -> float | None:
    """Parse a Retry-After header as bounded seconds, if present."""
    if not value:
        return None
    try:
        seconds = float(value)
    except ValueError:
        try:
            seconds = parsedate_to_datetime(value).timestamp() - time()
        except (TypeError, ValueError, OverflowError):
            return None
    return max(0.0, min(seconds, 60.0))
