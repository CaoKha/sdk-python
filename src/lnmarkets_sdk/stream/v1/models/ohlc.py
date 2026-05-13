"""OHLC topic payload."""

from __future__ import annotations

from pydantic import BaseModel

from lnmarkets_sdk.stream.v1._internal.models import BaseConfig


class OhlcData(BaseModel, BaseConfig):
    """Payload for `futures/inverse/{pair}/ohlc/{resolution}` topics."""

    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float


__all__ = ["OhlcData"]
