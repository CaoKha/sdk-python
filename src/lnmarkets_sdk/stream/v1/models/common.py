"""Common stream-v1 primitives shared across domains."""

from __future__ import annotations

from typing import Literal, cast

from pydantic import BaseModel, ConfigDict

type Pair = Literal["btc_usd"]
type Instrument = Literal["inverse"]
type MarginMode = Literal["isolated", "cross"]

type OhlcResolution = Literal[
    "1m",
    "3m",
    "5m",
    "10m",
    "15m",
    "30m",
    "45m",
    "1h",
    "2h",
    "3h",
    "4h",
    "1d",
    "1w",
    "1month",
    "3months",
]

type ExplicitTopic = Literal[
    "announcements",
    "wallet/deposit",
    "wallet/withdrawal",
    "futures/inverse/btc_usd/ticker",
    "futures/inverse/btc_usd/lastPrice",
    "futures/inverse/btc_usd/index",
    "futures/inverse/btc_usd/buckets",
    "futures/inverse/btc_usd/funding",
    "futures/inverse/btc_usd/isolated/trades",
    "futures/inverse/btc_usd/cross/orders",
    "futures/inverse/btc_usd/cross/position",
]

# Full enumeration of OHLC topics — Instrument × Pair × OhlcResolution.
type OhlcTopic = Literal[
    "futures/inverse/btc_usd/ohlc/1m",
    "futures/inverse/btc_usd/ohlc/3m",
    "futures/inverse/btc_usd/ohlc/5m",
    "futures/inverse/btc_usd/ohlc/10m",
    "futures/inverse/btc_usd/ohlc/15m",
    "futures/inverse/btc_usd/ohlc/30m",
    "futures/inverse/btc_usd/ohlc/45m",
    "futures/inverse/btc_usd/ohlc/1h",
    "futures/inverse/btc_usd/ohlc/2h",
    "futures/inverse/btc_usd/ohlc/3h",
    "futures/inverse/btc_usd/ohlc/4h",
    "futures/inverse/btc_usd/ohlc/1d",
    "futures/inverse/btc_usd/ohlc/1w",
    "futures/inverse/btc_usd/ohlc/1month",
    "futures/inverse/btc_usd/ohlc/3months",
]

type Topic = ExplicitTopic | OhlcTopic


def make_ohlc_topic(pair: Pair, resolution: OhlcResolution) -> OhlcTopic:
    """Build an OHLC topic string for the given pair and resolution.

    Python lacks template-literal types, so the computed `f"..."` is cast to
    `OhlcTopic`. Inputs are Literal-typed, so the resulting string is always
    a valid member of `OhlcTopic` by construction.
    """
    return cast("OhlcTopic", f"futures/inverse/{pair}/ohlc/{resolution}")


class ReconnectedEvent(BaseModel):
    """Payload emitted by the `reconnected` event."""

    model_config = ConfigDict(extra="forbid")

    attempts: int


__all__ = [
    "ExplicitTopic",
    "Instrument",
    "MarginMode",
    "OhlcResolution",
    "OhlcTopic",
    "Pair",
    "ReconnectedEvent",
    "Topic",
    "make_ohlc_topic",
]
