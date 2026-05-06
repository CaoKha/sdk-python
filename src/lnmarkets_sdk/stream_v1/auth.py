"""HMAC-SHA256 authentication for Stream V1."""

from __future__ import annotations

import base64
import hashlib
import hmac
import time
from typing import Literal


def get_hostname(network: Literal["mainnet", "testnet4"]) -> str:
    """Get Stream API hostname based on network."""
    if network == "testnet4":
        return "stream.testnet4.lnmarkets.com"
    return "stream.lnmarkets.com"


def get_websocket_url(network: Literal["mainnet", "testnet4"], hostname: str | None = None) -> str:
    """Get WebSocket URL for the given network."""
    if hostname:
        return f"wss://{hostname}/v1/stream"
    host = get_hostname(network)
    return f"wss://{host}/v1/stream"


def create_signature(secret: str, timestamp: str, nonce: str) -> str:
    """Create HMAC-SHA256 signature for Stream authentication.

    The signature is computed over the concatenation of timestamp and nonce,
    then base64-encoded.
    """
    payload = f"{timestamp}{nonce}"
    hashed = hmac.new(
        bytes(secret, "utf-8"),
        bytes(payload, "utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(hashed).decode("utf-8")


def generate_auth_params(
    key: str,
    secret: str,
    passphrase: str,
    extensions: list[str] | None = None,
) -> dict[str, str]:
    """Generate authentication parameters for Stream V1.

    Returns a dict with key, signature, timestamp, nonce, and passphrase
    suitable for passing to StreamClient.authenticate().
    """
    nonce: str = base64.b64encode(str(time.time_ns()).encode()).decode()
    timestamp = str(int(time.time() * 1000))
    signature = create_signature(secret, timestamp, nonce)

    params: dict[str, str] = {
        "key": key,
        "signature": signature,
        "timestamp": timestamp,
        "nonce": nonce,
        "passphrase": passphrase,
    }
    if extensions:
        params["extensions"] = str(extensions)
    return params
