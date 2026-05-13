"""Models for the subscribe / unsubscribe / unsubscribeAll RPC methods."""

from __future__ import annotations

from pydantic import BaseModel, Field

from lnmarkets_sdk.stream.v1._internal.models import BaseConfig
from lnmarkets_sdk.stream.v1.models.common import Topic


class SubscribeParams(BaseModel, BaseConfig):
    """Input for `client.subscription.subscribe(params)`."""

    topics: list[Topic] = Field(..., min_length=1)


class SubscribeResponse(BaseModel, BaseConfig):
    """Result of the `subscribe` RPC method."""

    subscribed: list[Topic]


class UnsubscribeParams(BaseModel, BaseConfig):
    """Input for `client.subscription.unsubscribe(params)`."""

    topics: list[Topic] = Field(..., min_length=1)


class UnsubscribeResponse(BaseModel, BaseConfig):
    """Result of the `unsubscribe` RPC method."""

    unsubscribed: list[Topic]


class UnsubscribeAllResponse(BaseModel, BaseConfig):
    """Result of the `unsubscribeAll` RPC method."""

    unsubscribed: list[Topic]


__all__ = [
    "SubscribeParams",
    "SubscribeResponse",
    "UnsubscribeAllResponse",
    "UnsubscribeParams",
    "UnsubscribeResponse",
]
