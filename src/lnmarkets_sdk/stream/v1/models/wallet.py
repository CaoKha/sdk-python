"""Wallet topic payloads (deposit, withdrawal)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from lnmarkets_sdk.stream.v1._internal.models import BaseConfig


class WalletDepositData(BaseModel, BaseConfig):
    """Payload for `wallet/deposit`."""

    currency: Literal["btc"]
    network: Literal["lightning", "bitcoin"]
    id: str
    amount: int
    balance: int
    status: str
    tx_id: str


class WalletWithdrawData(BaseModel, BaseConfig):
    """Payload for `wallet/withdrawal`."""

    currency: Literal["btc"]
    network: Literal["lightning", "bitcoin"]
    id: str
    amount: int
    fee: int
    balance: int
    status: str
    tx_id: str


__all__ = ["WalletDepositData", "WalletWithdrawData"]
