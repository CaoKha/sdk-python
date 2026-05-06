"""Stream V1 WebSocket client implementation."""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any, Literal

import websockets

from lnmarkets_sdk.stream_v1.auth import get_websocket_url
from lnmarkets_sdk.stream_v1.exceptions import (
    StreamDisconnectedError,
    StreamRequestTimeoutError,
    StreamRpcError,
)
from lnmarkets_sdk.stream_v1.models import (
    JsonRpcResponse,
    StreamClientConfig,
)

if TYPE_CHECKING:
    from collections.abc import Callable

REQUEST_TIMEOUT_MS = 10_000


class StreamClient:
    """Async WebSocket client for LN Markets Stream API v1.

    Implements JSON-RPC 2.0 over WebSocket with HMAC-SHA256 authentication.
    """

    def __init__(
        self,
        config: StreamClientConfig | None = None,
    ) -> None:
        """Initialize the Stream client.

        Args:
            config: Client configuration. Defaults to mainnet.

        Example:
        ```python
        from lnmarkets_sdk.stream_v1 import StreamClient

        async with StreamClient() as client:
            await client.connect()
            await client.authenticate(key="...", secret="...", passphrase="...")
            # use client...
        ```
        """
        if config is None:
            config = StreamClientConfig()
        self._config = config
        self._ws: Any = None
        self._state: ConnectionState = "disconnected"
        self._pending: dict[int, asyncio.Future[Any]] = {}
        self._id_counter = 0
        self._user_initiated_close = False
        self._reconnect_attempts = 0
        self._reconnect_timer: asyncio.TimerHandle | None = None
        self._listeners: dict[str, set[Callable[..., Any]]] = {}

    @property
    def state(self) -> ConnectionState:
        """Current connection state."""
        return self._state

    async def connect(self) -> None:
        """Connect to the LN Markets Stream WebSocket server.

        Raises:
            StreamDisconnectedError: If already connected or reconnecting.
        """
        if self._state != "disconnected":
            msg = f"Cannot connect(): state is '{self._state}'"
            raise StreamDisconnectedError(msg)
        self._user_initiated_close = False
        await self._open_websocket()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        self._user_initiated_close = True
        if self._reconnect_timer is not None:
            self._reconnect_timer.cancel()
            self._reconnect_timer = None
        if self._ws is not None and self._state != "disconnected":
            await self._ws.close(1000)
        self._state = "disconnected"

    async def authenticate(
        self,
        key: str,
        secret: str,
        passphrase: str,
        extensions: list[str] | None = None,
    ) -> Any:
        """Authenticate with the Stream API.

        Args:
            key: API key.
            secret: API secret.
            passphrase: API passphrase.
            extensions: Optional list of permission extensions.

        Returns:
            Authentication result with permissions.
        """
        return await self.request(
            "authenticate",
            {
                "key": key,
                "secret": secret,
                "passphrase": passphrase,
                "nonce": str(hash((key, secret, passphrase))),
                "timestamp": str(int(asyncio.get_event_loop().time() * 1000)),
                "extensions": extensions or [],
            },
        )

    async def time(self) -> str:
        """Get server time.

        Returns:
            Server timestamp as string.
        """
        result = await self.request("time", {})
        return str(result)

    async def ping(self) -> Any:
        """Ping the server.

        Returns:
            Ping response.
        """
        return await self.request("ping", {})

    async def whoami(self) -> Any:
        """Get authenticated user info.

        Returns:
            User information.
        """
        return await self.request("whoami", {})

    async def request(
        self,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any] | str | int | bool | None:
        """Send a JSON-RPC request and wait for response.

        Args:
            method: JSON-RPC method name.
            params: Method parameters.

        Returns:
            Response result.

        Raises:
            StreamDisconnectedError: If not connected.
            StreamRequestTimeoutError: If request times out.
            StreamRpcError: If server returns an error.
        """
        if self._state != "connected" or self._ws is None:
            raise StreamDisconnectedError("request")

        self._id_counter += 1
        id = self._id_counter

        payload = json.dumps(
            {"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}},
            separators=(",", ":"),
        )

        future: asyncio.Future[Any] = asyncio.get_event_loop().create_future()

        async def timeout_handler() -> None:
            await asyncio.sleep(REQUEST_TIMEOUT_MS / 1000)
            if not future.done():
                future.cancel()
                self._pending.pop(id, None)

        timeout_task = asyncio.create_task(timeout_handler())

        self._pending[id] = future

        try:
            await self._ws.send(payload)
            result = await future
            timeout_task.cancel()
            return result
        except asyncio.CancelledError:
            timeout_task.cancel()
            raise StreamRequestTimeoutError(method) from None

    async def _open_websocket(self) -> None:
        """Open the WebSocket connection."""
        url = get_websocket_url(self._config.network, self._config.hostname)
        self._state = "reconnecting" if self._reconnect_attempts > 0 else "connecting"

        try:
            self._ws = await websockets.connect(url)
            self._state = "connected"
            self._reconnect_attempts = 0
            asyncio.create_task(self._receive_loop())
        except Exception:
            self._ws = None
            self._state = "disconnected"
            if self._should_reconnect():
                self._schedule_reconnect()
            raise

    async def _receive_loop(self) -> None:
        """Receive and dispatch messages from WebSocket."""
        if self._ws is None:
            return

        try:
            async for raw_msg in self._ws:
                await self._on_message(raw_msg)
        except websockets.ConnectionClosed:
            pass
        finally:
            self._state = "disconnected"
            self._reject_pending()
            if not self._user_initiated_close and self._should_reconnect():
                self._schedule_reconnect()

    async def _on_message(self, raw_msg: str) -> None:
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(raw_msg)
        except json.JSONDecodeError:
            return

        if not isinstance(data, dict):
            return

        if data.get("method") == "subscription":
            params = data.get("params", {})
            topic = params.get("topic") if isinstance(params, dict) else None
            if isinstance(topic, str):
                await self._emit(topic, params.get("data"))
            return

        if "id" in data:
            response = JsonRpcResponse.model_validate(data)
            future = self._pending.pop(response.id, None)
            if future is not None:
                if response.error is not None:
                    future.set_exception(
                        StreamRpcError(
                            response.error.code,
                            response.error.message,
                            response.error.data,
                        ),
                    )
                else:
                    future.set_result(response.result)

    def _should_reconnect(self) -> bool:
        """Check if reconnection should be attempted."""
        return self._config.reconnect_enabled and not self._user_initiated_close

    def _schedule_reconnect(self) -> None:
        """Schedule a reconnection attempt."""
        if self._reconnect_attempts >= self._config.max_reconnect_attempts:
            self._state = "disconnected"
            return

        self._state = "reconnecting"
        loop = asyncio.get_event_loop()
        self._reconnect_timer = loop.call_later(
            self._config.reconnect_interval,
            lambda: asyncio.create_task(self._do_reconnect()),
        )

    async def _do_reconnect(self) -> None:
        """Perform the reconnection."""
        import contextlib

        self._reconnect_timer = None
        self._reconnect_attempts += 1
        with contextlib.suppress(Exception):
            await self._open_websocket()

    def _reject_pending(self) -> None:
        """Reject all pending requests."""
        for future in self._pending.values():
            if not future.done():
                future.set_exception(StreamDisconnectedError("pending request"))
        self._pending.clear()

    async def _emit(self, event: str, data: Any) -> None:
        """Emit an event to registered listeners."""
        import inspect

        listeners = self._listeners.get(event, set())
        for listener in listeners:
            try:
                result = listener(data)
                if inspect.iscoroutine(result):
                    await result
            except Exception:
                pass


ConnectionState = Literal["disconnected", "connecting", "connected", "reconnecting"]
