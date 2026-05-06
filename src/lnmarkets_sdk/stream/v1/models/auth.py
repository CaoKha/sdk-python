"""Models for the authenticate / whoami RPC methods."""

from __future__ import annotations

from pydantic import BaseModel, Field

from lnmarkets_sdk.stream.v1._internal.models import BaseConfig


class AuthenticateParams(BaseModel, BaseConfig):
    """Input for `client.auth.authenticate(params)`."""

    key: str = Field(..., min_length=1)
    secret: str = Field(..., min_length=1)
    passphrase: str = Field(..., min_length=1)


class AuthenticateResponse(BaseModel, BaseConfig):
    """Result of the `authenticate` RPC method."""

    authenticated: bool
    permissions: list[str]


class WhoamiResponse(BaseModel, BaseConfig):
    """Result of the `whoami` RPC method."""

    api_key: str
    user_id: str
    permissions: list[str]


__all__ = [
    "AuthenticateParams",
    "AuthenticateResponse",
    "WhoamiResponse",
]
