"""Isolated futures trade events (`futures/inverse/btc_usd/isolated/trades`)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from lnmarkets_sdk.stream.v1._internal.models import BaseConfig
from lnmarkets_sdk.stream.v1.models.common import Pair


class IsolatedTradeOpenPayload(BaseModel, BaseConfig):
    id: str
    side: Literal["buy", "sell"]
    type: Literal["limit"]
    quantity: int
    margin: int
    leverage: float
    price: float
    opening_fee: int
    created_at: int
    client_id: str | None = None


class IsolatedTradeOpen(BaseModel, BaseConfig):
    pair: Pair
    event: Literal["open"]
    trade: IsolatedTradeOpenPayload


class IsolatedTradeFilledPayload(BaseModel, BaseConfig):
    id: str
    side: Literal["buy", "sell"]
    type: Literal["limit", "market"]
    quantity: int
    margin: int
    leverage: float
    price: float
    opening_fee: int
    created_at: int
    client_id: str | None = None


class IsolatedTradeFilled(BaseModel, BaseConfig):
    pair: Pair
    event: Literal["filled"]
    trade: IsolatedTradeFilledPayload


class IsolatedTradeClosedPayload(BaseModel, BaseConfig):
    id: str
    closed_at: int
    closing_fee: int
    pl: int
    exit_price: float
    client_id: str | None = None


class IsolatedTradeClosed(BaseModel, BaseConfig):
    pair: Pair
    event: Literal["closed"]
    trade: IsolatedTradeClosedPayload


class IsolatedTradeCanceledPayload(BaseModel, BaseConfig):
    id: str
    closed_at: int
    client_id: str | None = None


class IsolatedTradeCanceled(BaseModel, BaseConfig):
    pair: Pair
    event: Literal["canceled"]
    trade: IsolatedTradeCanceledPayload


class IsolatedTradeLiquidationPayload(BaseModel, BaseConfig):
    id: str
    closed_at: int
    closing_fee: int
    exit_price: float
    client_id: str | None = None


class IsolatedTradeLiquidation(BaseModel, BaseConfig):
    pair: Pair
    event: Literal["liquidation"]
    trade: IsolatedTradeLiquidationPayload


class IsolatedTradeStoplossPayload(BaseModel, BaseConfig):
    id: str
    closed_at: int
    closing_fee: int
    pl: int
    exit_price: float
    client_id: str | None = None


class IsolatedTradeStoploss(BaseModel, BaseConfig):
    pair: Pair
    event: Literal["stoploss"]
    trade: IsolatedTradeStoplossPayload


class IsolatedTradeTakeprofitPayload(BaseModel, BaseConfig):
    id: str
    closed_at: int
    closing_fee: int
    pl: int
    exit_price: float
    client_id: str | None = None


class IsolatedTradeTakeprofit(BaseModel, BaseConfig):
    pair: Pair
    event: Literal["takeprofit"]
    trade: IsolatedTradeTakeprofitPayload


class IsolatedTradeFundingPayload(BaseModel, BaseConfig):
    id: str
    margin: int
    liquidation_price: float
    funding_fee: int
    funded_at: int
    client_id: str | None = None


class IsolatedTradeFunding(BaseModel, BaseConfig):
    pair: Pair
    event: Literal["funding"]
    trade: IsolatedTradeFundingPayload


type IsolatedTradesEvent = (
    IsolatedTradeOpen
    | IsolatedTradeFilled
    | IsolatedTradeClosed
    | IsolatedTradeCanceled
    | IsolatedTradeLiquidation
    | IsolatedTradeStoploss
    | IsolatedTradeTakeprofit
    | IsolatedTradeFunding
)


__all__ = [
    "IsolatedTradeCanceled",
    "IsolatedTradeCanceledPayload",
    "IsolatedTradeClosed",
    "IsolatedTradeClosedPayload",
    "IsolatedTradeFilled",
    "IsolatedTradeFilledPayload",
    "IsolatedTradeFunding",
    "IsolatedTradeFundingPayload",
    "IsolatedTradeLiquidation",
    "IsolatedTradeLiquidationPayload",
    "IsolatedTradeOpen",
    "IsolatedTradeOpenPayload",
    "IsolatedTradeStoploss",
    "IsolatedTradeStoplossPayload",
    "IsolatedTradeTakeprofit",
    "IsolatedTradeTakeprofitPayload",
    "IsolatedTradesEvent",
]
