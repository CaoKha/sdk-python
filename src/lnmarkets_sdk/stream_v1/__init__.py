"""LN Markets Stream V1 WebSocket client.

Example:
```python
from lnmarkets_sdk.stream_v1 import StreamClient

async with StreamClient() as client:
    await client.connect()
    await client.authenticate(key="...", secret="...", passphrase="...")
    result = await client.ping()
    print(result)
```
"""

from lnmarkets_sdk.stream_v1.auth import get_hostname, get_websocket_url
from lnmarkets_sdk.stream_v1.client import ConnectionState, StreamClient
from lnmarkets_sdk.stream_v1.exceptions import (
    ReconnectFailedError,
    StreamDisconnectedError,
    StreamRequestTimeoutError,
    StreamRpcError,
)
from lnmarkets_sdk.stream_v1.models import (
    AuthenticateParams,
    AuthenticateResult,
    JsonRpcErrorResponse,
    JsonRpcRequest,
    JsonRpcResponse,
    JsonRpcSubscriptionNotification,
    StreamClientConfig,
    SubscriptionParams,
    WhoamiResult,
)

__all__ = [
    "AuthenticateParams",
    "AuthenticateResult",
    "ConnectionState",
    "get_hostname",
    "get_websocket_url",
    "JsonRpcErrorResponse",
    "JsonRpcRequest",
    "JsonRpcResponse",
    "JsonRpcSubscriptionNotification",
    "ReconnectFailedError",
    "StreamClient",
    "StreamClientConfig",
    "StreamDisconnectedError",
    "StreamRequestTimeoutError",
    "StreamRpcError",
    "SubscriptionParams",
    "WhoamiResult",
]
