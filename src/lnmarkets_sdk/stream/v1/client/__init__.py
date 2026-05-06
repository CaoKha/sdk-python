"""Public stream-v1 client (mirror of rest_v3.http.client.LNMClient)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from types import UnionType
from typing import Any, Literal, TypedDict, overload

from pydantic import BaseModel

from lnmarkets_sdk.stream.v1._internal import StreamInstance
from lnmarkets_sdk.stream.v1._internal.models import (
    ConnectionState,
    StreamClientConfig,
)
from lnmarkets_sdk.stream.v1.models.common import Topic

from .auth import AuthClient
from .public import PublicClient
from .subscription import SubscriptionClient

Listener = Callable[..., object | Awaitable[object]]


# ---------------------------------------------------------------------------
# Typed listener signatures — used by overloads on `StreamClient.on(...)`.
# Mirrors the TS SDK's `EventEmitter<StreamEvents>` mapped types so callers
# get inferred lambda parameter types instead of `Unknown`.
# ---------------------------------------------------------------------------


class ReconnectedEventPayload(TypedDict):
    """Payload dispatched on the `reconnected` lifecycle event."""

    attempts: int


OpenListener = Callable[[], None | Awaitable[None]]
CloseListener = Callable[[int, str], None | Awaitable[None]]
ErrorListener = Callable[[BaseException], None | Awaitable[None]]
ReconnectedListener = Callable[[ReconnectedEventPayload], None | Awaitable[None]]
TopicListener = Callable[[dict[str, Any]], None | Awaitable[None]]


class StreamClient:
    """Async WebSocket client for LN Markets Stream API v1.

    Composes domain clients (`public`, `auth`, `subscription`) over a shared
    `StreamInstance` transport. Mirrors the layout of `rest_v3.LNMClient`.

    Example:
    ```python
    from lnmarkets_sdk.stream.v1 import StreamClient
    from lnmarkets_sdk.stream.v1.models import (
        AuthenticateParams,
        SubscribeParams,
    )

    async with StreamClient() as client:
        await client.connect()

        await client.auth.authenticate(
            AuthenticateParams(key=k, secret=s, passphrase=p),
        )

        await client.subscription.subscribe(
            SubscribeParams(topics=["futures/inverse/btc_usd/ticker"]),
        )
        client.on("futures/inverse/btc_usd/ticker", lambda data: print(data))

        pong = await client.public.ping()
    ```
    """

    def __init__(self, config: StreamClientConfig | None = None) -> None:
        self._instance = StreamInstance(config)
        self.public = PublicClient(self)
        self.auth = AuthClient(self)
        self.subscription = SubscriptionClient(self)

    async def __aenter__(self) -> StreamClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    @property
    def state(self) -> ConnectionState:
        return self._instance.state

    async def connect(self) -> None:
        await self._instance.connect()

    async def close(self) -> None:
        await self._instance.close()

    @overload
    def on(self, event: Literal["open"], listener: OpenListener) -> None: ...
    @overload
    def on(self, event: Literal["close"], listener: CloseListener) -> None: ...
    @overload
    def on(self, event: Literal["error"], listener: ErrorListener) -> None: ...
    @overload
    def on(
        self, event: Literal["reconnected"], listener: ReconnectedListener
    ) -> None: ...
    @overload
    def on(self, event: Topic, listener: TopicListener) -> None: ...
    def on(self, event: str, listener: Listener) -> None:
        """Register a listener for a topic or lifecycle event.

        Lifecycle events: `open`, `close`, `error`, `reconnected`.
        Listener parameter types are inferred per event via overloads:
        - `open`        -> `()`
        - `close`       -> `(code: int, reason: str)`
        - `error`       -> `(err: BaseException)`
        - `reconnected` -> `(event: ReconnectedEventPayload)`
        - Topic events  -> `(data: dict[str, Any])`
        """
        self._instance.on(event, listener)

    def off(self, event: str, listener: Listener) -> None:
        self._instance.off(event, listener)

    def remove_all_listeners(self, event: str | None = None) -> None:
        self._instance.remove_all_listeners(event)

    async def request[T](
        self,
        method: str,
        params: BaseModel | dict[str, Any] | None = None,
        response_model: type[T] | UnionType | None = None,
    ) -> T:
        """Send a JSON-RPC request through the underlying transport.

        Pydantic params are dumped via `model_dump(by_alias=True, exclude_none=True)`
        so wire fields use camelCase.
        """
        params_dict: Any | None
        if isinstance(params, BaseModel):
            params_dict = params.model_dump(
                mode="json", exclude_none=True, by_alias=True
            )
        else:
            params_dict = params
        return await self._instance.request(
            method, params=params_dict, response_model=response_model
        )


def create_stream_client(config: StreamClientConfig | None = None) -> StreamClient:
    """Factory mirroring `createStreamClient(options)` in the TS SDK."""
    return StreamClient(config)


__all__ = [
    "CloseListener",
    "ErrorListener",
    "OpenListener",
    "ReconnectedEventPayload",
    "ReconnectedListener",
    "StreamClient",
    "TopicListener",
    "create_stream_client",
]
