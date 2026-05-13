"""Public RPC methods (hello, ping, time)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from lnmarkets_sdk.stream.v1.models.lifecycle import (
    HelloParams,
    HelloResponse,
    PingResponse,
    TimeResponse,
)

if TYPE_CHECKING:
    from lnmarkets_sdk.stream.v1.client import StreamClient


class PublicClient:
    """Client for unauthenticated RPC methods."""

    def __init__(self, client: StreamClient) -> None:
        self._client = client

    async def hello(self, params: HelloParams) -> HelloResponse:
        """Send a `hello` handshake.

        Example:
        ```python
        from lnmarkets_sdk.stream.v1 import create_stream_client
        from lnmarkets_sdk.stream.v1.models import HelloParams

        async with create_stream_client() as client:
            await client.connect()
            result = await client.public.hello(
                HelloParams(client_name="my-bot", client_version="1.0.0"),
            )
            print(result.version)
        ```
        """
        return await self._client.request(
            "hello",
            params=params,
            response_model=HelloResponse,
        )

    async def ping(self) -> PingResponse:
        """Ping the server. Returns the literal string `'pong'`."""
        result: Any = await self._client.request("ping")
        return cast(PingResponse, result)

    async def time(self) -> TimeResponse:
        """Get the server time."""
        return await self._client.request("time", response_model=TimeResponse)


__all__ = ["PublicClient"]
