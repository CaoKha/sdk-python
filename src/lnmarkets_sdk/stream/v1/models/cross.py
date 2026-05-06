"""Cross futures order and position events."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from lnmarkets_sdk.stream.v1._internal.models import BaseConfig
from lnmarkets_sdk.stream.v1.models.common import Pair


class CrossOrderOpenPayload(BaseModel, BaseConfig):
    id: str
    side: Literal["buy", "sell"]
    type: Literal["limit"]
    quantity: int
    price: float
    trading_fee: int
    client_id: str | None = None
    created_at: int


class CrossOrderFilledPayload(BaseModel, BaseConfig):
    id: str
    side: Literal["buy", "sell"]
    type: Literal["limit", "liquidation", "market"]
    quantity: int
    price: float
    trading_fee: int
    client_id: str | None = None
    created_at: int
    filled_at: int


class CrossOrderCanceledPayload(BaseModel, BaseConfig):
    id: str
    side: Literal["buy", "sell"]
    type: Literal["limit"]
    quantity: int
    price: float
    client_id: str | None = None
    created_at: int
    canceled_at: int


class CrossOrderNew(BaseModel, BaseConfig):
    pair: Pair
    event: Literal["new"]
    order: CrossOrderOpenPayload | CrossOrderFilledPayload


class CrossOrderLimit(BaseModel, BaseConfig):
    pair: Pair
    event: Literal["limit"]
    order: CrossOrderFilledPayload


class CrossOrderCanceled(BaseModel, BaseConfig):
    pair: Pair
    event: Literal["canceled"]
    order: CrossOrderCanceledPayload


type CrossOrderEvent = CrossOrderNew | CrossOrderLimit | CrossOrderCanceled


class CrossPositionPayload(BaseModel, BaseConfig):
    quantity: int
    leverage: float
    margin: int
    entry_price: float | None = None
    liquidation: float | None = None
    total_pl: int
    funding_fees: int
    trading_fees: int
    initial_margin: int
    maintenance_margin: int
    running_margin: int
    delta_pl: int
    updated_at: int


class CrossPositionData(BaseModel, BaseConfig):
    """Payload for `futures/inverse/btc_usd/cross/position`."""

    pair: Pair
    event: Literal[
        "new",
        "limit",
        "cancel",
        "leverage",
        "deposit",
        "withdraw",
        "liquidation",
        "funding",
    ]
    position: CrossPositionPayload


__all__ = [
    "CrossOrderCanceled",
    "CrossOrderCanceledPayload",
    "CrossOrderEvent",
    "CrossOrderFilledPayload",
    "CrossOrderLimit",
    "CrossOrderNew",
    "CrossOrderOpenPayload",
    "CrossPositionData",
    "CrossPositionPayload",
]
