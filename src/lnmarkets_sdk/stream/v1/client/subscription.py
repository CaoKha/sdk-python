"""Subscription RPC methods (subscribe, unsubscribe, unsubscribe_all)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from lnmarkets_sdk.stream.v1.models.subscription import (
    SubscribeParams,
    SubscribeResponse,
    UnsubscribeAllResponse,
    UnsubscribeParams,
    UnsubscribeResponse,
)

if TYPE_CHECKING:
    from lnmarkets_sdk.stream.v1.client import StreamClient


class SubscriptionClient:
    """Client for managing topic subscriptions."""

    def __init__(self, client: StreamClient) -> None:
        self._client = client

    async def subscribe(self, params: SubscribeParams) -> SubscribeResponse:
        """Subscribe to one or more topics.

        Example:
        ```python
        from lnmarkets_sdk.stream.v1 import create_stream_client
        from lnmarkets_sdk.stream.v1.models import SubscribeParams

        async with create_stream_client() as client:
            await client.connect()
            await client.subscription.subscribe(
                SubscribeParams(topics=["futures/inverse/btc_usd/ticker"]),
            )
        ```
        """
        return await self._client.request(
            "subscribe",
            params=params,
            response_model=SubscribeResponse,
        )

    async def unsubscribe(self, params: UnsubscribeParams) -> UnsubscribeResponse:
        """Unsubscribe from one or more topics."""
        return await self._client.request(
            "unsubscribe",
            params=params,
            response_model=UnsubscribeResponse,
        )

    async def unsubscribe_all(self) -> UnsubscribeAllResponse:
        """Unsubscribe from every active topic."""
        return await self._client.request(
            "unsubscribeAll",
            response_model=UnsubscribeAllResponse,
        )


__all__ = ["SubscriptionClient"]
