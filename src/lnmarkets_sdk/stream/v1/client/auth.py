"""Authentication RPC methods (authenticate, whoami)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from lnmarkets_sdk.stream.v1._internal.models import StreamAuthContext
from lnmarkets_sdk.stream.v1._internal.utils import generate_auth_params
from lnmarkets_sdk.stream.v1.models.auth import (
    AuthenticateParams,
    AuthenticateResponse,
    WhoamiResponse,
)

if TYPE_CHECKING:
    from lnmarkets_sdk.stream.v1.client import StreamClient


class AuthClient:
    """Client for authentication RPC methods."""

    def __init__(self, client: StreamClient) -> None:
        self._client = client

    async def authenticate(self, params: AuthenticateParams) -> AuthenticateResponse:
        """Authenticate with the Stream API.

        Example:
        ```python
        from lnmarkets_sdk.stream.v1 import create_stream_client
        from lnmarkets_sdk.stream.v1.models import AuthenticateParams

        async with create_stream_client() as client:
            await client.connect()
            await client.auth.authenticate(
                AuthenticateParams(key=k, secret=s, passphrase=p),
            )
        ```
        """
        auth = StreamAuthContext(
            key=params.key, secret=params.secret, passphrase=params.passphrase
        )
        return await self._client.request(
            "authenticate",
            params=generate_auth_params(auth),
            response_model=AuthenticateResponse,
        )

    async def whoami(self) -> WhoamiResponse:
        """Return information about the authenticated user."""
        return await self._client.request(
            "whoami",
            response_model=WhoamiResponse,
        )


__all__ = ["AuthClient"]
