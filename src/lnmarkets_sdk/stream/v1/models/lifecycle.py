"""Models for lifecycle RPC methods (hello / ping / time)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from lnmarkets_sdk.stream.v1._internal.models import BaseConfig


class HelloParams(BaseModel, BaseConfig):
    """Input for `client.public.hello(params)`."""

    client_name: str
    client_version: str


class HelloResponse(BaseModel, BaseConfig):
    """Result of the `hello` RPC method."""

    version: Literal["1.0.0"]


PingResponse = Literal["pong"]


class TimeResponse(BaseModel, BaseConfig):
    """Result of the `time` RPC method."""

    time: int


__all__ = [
    "HelloParams",
    "HelloResponse",
    "PingResponse",
    "TimeResponse",
]
