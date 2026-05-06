"""Futures topic payloads (ticker, lastPrice, index, buckets, funding)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from lnmarkets_sdk.stream.v1._internal.models import BaseConfig
from lnmarkets_sdk.stream.v1.models.common import Pair


class FundingTime(BaseModel, BaseConfig):
    rate: float | None = Field(default=None)
    time: int | None = Field(default=None)


class FuturesTickerData(BaseModel, BaseConfig):
    """Payload for `futures/inverse/btc_usd/ticker`."""

    time: int
    last_price: float | None = None
    index: float | None = None
    funding: FundingTime


class FuturesLastPriceData(BaseModel, BaseConfig):
    """Payload for `futures/inverse/btc_usd/lastPrice`."""

    time: int
    last_price: float


class FuturesIndexData(BaseModel, BaseConfig):
    """Payload for `futures/inverse/btc_usd/index`."""

    time: int
    index: float


class FuturesBucket(BaseModel, BaseConfig):
    min_size: int
    max_size: int
    ask_price: float | None = None
    bid_price: float | None = None


class FuturesBucketData(BaseModel, BaseConfig):
    """Payload for `futures/inverse/btc_usd/buckets`."""

    time: int
    buckets: list[FuturesBucket]


class FuturesFundingData(BaseModel, BaseConfig):
    """Payload for `futures/inverse/btc_usd/funding`."""

    pair: Pair
    current: FundingTime


__all__ = [
    "FundingTime",
    "FuturesBucket",
    "FuturesBucketData",
    "FuturesFundingData",
    "FuturesIndexData",
    "FuturesLastPriceData",
    "FuturesTickerData",
]
