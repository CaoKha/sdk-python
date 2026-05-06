"""LN Markets Stream V1 WebSocket client.

Layout mirrors `rest_v3`:

- `_internal/`: WebSocket transport, JSON-RPC framing, config, exceptions.
- `models/`: pydantic models per domain (futures, isolated, cross, ohlc,
  wallet, announcements, lifecycle, auth, subscription, common).
- `client/`: `StreamClient` composing `public`, `auth`, `subscription`
  domain clients.

Example:
```python
import asyncio
from lnmarkets_sdk.stream.v1 import StreamClient, StreamClientConfig
from lnmarkets_sdk.stream.v1.models import (
    AuthenticateParams,
    SubscribeParams,
)

async def main():
    config = StreamClientConfig(network="testnet4")
    async with StreamClient(config) as client:
        await client.connect()
        await client.auth.authenticate(
            AuthenticateParams(key=k, secret=s, passphrase=p),
        )
        await client.subscription.subscribe(
            SubscribeParams(topics=["futures/inverse/btc_usd/ticker"]),
        )
        client.on(
            "futures/inverse/btc_usd/ticker",
            lambda data: print(data),
        )
        await asyncio.sleep(30)

asyncio.run(main())
```
"""

from lnmarkets_sdk.stream.v1._internal.models import (
    ConnectionState,
    ReconnectFailedError,
    StreamAuthContext,
    StreamClientConfig,
    StreamDisconnectedError,
    StreamException,
    StreamRequestTimeoutError,
    StreamRpcError,
    StreamValidationException,
)
from lnmarkets_sdk.stream.v1._internal.utils import (
    create_signature,
    generate_auth_params,
    get_hostname,
    get_websocket_url,
)
from lnmarkets_sdk.stream.v1.client import StreamClient, create_stream_client

__all__ = [
    "ConnectionState",
    "ReconnectFailedError",
    "StreamAuthContext",
    "StreamClient",
    "StreamClientConfig",
    "StreamDisconnectedError",
    "StreamException",
    "StreamRequestTimeoutError",
    "StreamRpcError",
    "StreamValidationException",
    "create_signature",
    "create_stream_client",
    "generate_auth_params",
    "get_hostname",
    "get_websocket_url",
]
