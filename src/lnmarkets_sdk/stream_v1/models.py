"""Pydantic models for Stream V1 JSON-RPC protocol."""

from __future__ import annotations

from typing import Any, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class BaseConfig:
    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


T = TypeVar("T")


class JsonRpcRequest(BaseModel, BaseConfig):
    jsonrpc: Literal["2.0"] = "2.0"
    id: int
    method: str
    params: dict[str, Any] | None = None


class JsonRpcResponse(BaseModel, BaseConfig):
    id: int
    jsonrpc: Literal["2.0"] = "2.0"
    result: dict[str, Any] | list[Any] | str | int | bool | None = None
    error: JsonRpcErrorResponse | None = None


class JsonRpcErrorResponse(BaseModel, BaseConfig):
    code: int
    message: str
    data: dict[str, Any] | list[Any] | str | int | bool | None = None


class JsonRpcSubscriptionNotification(BaseModel, BaseConfig):
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["subscription"]
    params: SubscriptionParams


class SubscriptionParams(BaseModel, BaseConfig):
    topic: str
    data: dict[str, Any] | list[Any] | str | int | bool | None = None


class AuthenticateParams(BaseModel, BaseConfig):
    key: str
    signature: str
    timestamp: str
    nonce: str
    passphrase: str | None = None
    extensions: list[str] | None = None


class AuthenticateResult(BaseModel, BaseConfig):
    permissions: list[str]
    user_id: str | None = None
    alias: str | None = None


class WhoamiResult(BaseModel, BaseConfig):
    permissions: list[str]
    user_id: str | None = None
    alias: str | None = None


class StreamClientConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    network: Literal["mainnet", "testnet4"] = "mainnet"
    reconnect_interval: float = Field(default=5.0, gt=0)
    reconnect_enabled: bool = True
    max_reconnect_attempts: int = Field(default=5, ge=0)
    hostname: str | None = None


__all__ = [
    "AuthenticateParams",
    "AuthenticateResult",
    "BaseConfig",
    "JsonRpcErrorResponse",
    "JsonRpcRequest",
    "JsonRpcResponse",
    "JsonRpcSubscriptionNotification",
    "StreamClientConfig",
    "SubscriptionParams",
    "WhoamiResult",
]
