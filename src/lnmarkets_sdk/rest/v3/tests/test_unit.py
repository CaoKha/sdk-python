"""Unit tests for request transport and param serialization (no network).

Each test drives a real client method against a mocked HTTP transport and
asserts how the request goes out on the wire: the HTTP method, path, and
whether params land in the query string (GET/DELETE) or a JSON body (POST/PUT).
"""

import hashlib
import hmac
import json
from base64 import b64encode
from urllib.parse import urlencode

from pytest_httpx import HTTPXMock

from lnmarkets_sdk.rest.v3._internal.utils import prepare_params
from lnmarkets_sdk.rest.v3.http.client import (
    APIAuthContext,
    APIClientConfig,
    LNMClient,
)
from lnmarkets_sdk.rest.v3.models.futures_isolated import (
    FuturesOrder,
    GetClosedTradesParams,
    RemoveStoplossParams,
    RemoveTakeprofitParams,
    UpdateStoplossParams,
)

TRADE_ID = "d0b9f9a0-4f6e-4a5a-8b7a-7f0f5f9a8a1e"
SECRET = "test-secret"


def _auth_config() -> APIClientConfig:
    return APIClientConfig(
        network="testnet4",
        authentication=APIAuthContext(
            key="test-key",
            secret=SECRET,
            passphrase="test-passphrase",
        ),
    )


def _running_trade_payload() -> dict[str, object]:
    """Full open-or-running trade response (camelCase, as the API returns it)."""
    return {
        "id": TRADE_ID,
        "type": "market",
        "side": "buy",
        "openingFee": 0,
        "closingFee": 0,
        "maintenanceMargin": 100,
        "quantity": 1,
        "margin": 1000,
        "leverage": 10,
        "price": 100_000,
        "liquidation": 90_000,
        "stoploss": 0,
        "stoplossTrailingDistance": 0.1,
        "takeprofit": 0,
        "exitPrice": None,
        "pl": 0,
        "createdAt": "2026-01-01T00:00:00.000Z",
        "filledAt": "2026-01-01T00:00:01.000Z",
        "closedAt": None,
        "entryPrice": 100_000,
        "entryMargin": 1000,
        "open": False,
        "running": True,
        "canceled": False,
        "closed": False,
        "sumFundingFees": 0,
        "sumCashInPl": 0,
        "sumCashInMargin": 0,
        "clientId": None,
    }


def test_update_stoploss_params_serialize_mode() -> None:
    # Mode defaults to "fixed" when omitted.
    fixed = prepare_params(UpdateStoplossParams(id=TRADE_ID, value=50_000))
    assert fixed == {"id": TRADE_ID, "value": 50_000, "mode": "fixed"}

    # Trailing mode carries a fractional distance as `value`.
    trailing = prepare_params(
        UpdateStoplossParams(id=TRADE_ID, value=0.1, mode="trailing")
    )
    assert trailing is not None
    assert trailing["mode"] == "trailing"
    assert trailing["value"] == 0.1


async def test_get_running_trades_issues_plain_get(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(json=[])

    async with LNMClient(_auth_config()) as client:
        await client.futures.isolated.get_running_trades()

    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "GET"
    assert request.url.path == "/v3/futures/isolated/trades/running"
    assert request.url.query == b""
    assert request.read() == b""


async def test_get_closed_trades_sends_query_params(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(json={"data": [], "nextCursor": None})

    async with LNMClient(_auth_config()) as client:
        await client.futures.isolated.get_closed_trades(GetClosedTradesParams(limit=10))

    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "GET"
    assert request.url.path == "/v3/futures/isolated/trades/closed"
    # Params go in the query string, not a body.
    assert request.url.params["limit"] == "10"
    assert request.read() == b""


async def test_new_trade_posts_json_body(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(json=_running_trade_payload())

    async with LNMClient(_auth_config()) as client:
        await client.futures.isolated.new_trade(
            FuturesOrder(type="market", side="buy", quantity=1, leverage=10)
        )

    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "POST"
    assert request.url.path == "/v3/futures/isolated/trade"
    assert request.url.query == b""
    # Params go in the JSON body.
    assert request.headers["content-type"] == "application/json"
    body = json.loads(request.read())
    assert body["type"] == "market"
    assert body["side"] == "buy"


async def test_update_stoploss_trailing_puts_json_body(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(json=_running_trade_payload())

    async with LNMClient(_auth_config()) as client:
        await client.futures.isolated.update_stoploss(
            UpdateStoplossParams(id=TRADE_ID, value=0.1, mode="trailing")
        )

    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "PUT"
    assert request.url.path == "/v3/futures/isolated/trade/stoploss"
    body = json.loads(request.read())
    assert body == {"id": TRADE_ID, "value": 0.1, "mode": "trailing"}


async def test_remove_stoploss_uses_delete_with_query_params(
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(json=_running_trade_payload())

    async with LNMClient(_auth_config()) as client:
        result = await client.futures.isolated.remove_stoploss(
            RemoveStoplossParams(id=TRADE_ID)
        )

    # Response parses into the model, including the new trailing-distance field.
    assert str(result.id) == TRADE_ID
    assert result.stoploss_trailing_distance == 0.1

    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "DELETE"
    # `id` travels in the query string, not the body.
    assert request.url.params["id"] == TRADE_ID
    assert request.read() == b""

    # Signature is signed over the query string (server uses `data = body ?? url.search`).
    query = f"?{urlencode({'id': TRADE_ID})}"
    timestamp = request.headers["lnm-access-timestamp"]
    payload = f"{timestamp}delete/v3/futures/isolated/trade/stoploss{query}"
    expected = b64encode(
        hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    ).decode()
    assert request.headers["lnm-access-signature"] == expected


async def test_remove_takeprofit_uses_delete_with_query_params(
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(json=_running_trade_payload())

    async with LNMClient(_auth_config()) as client:
        await client.futures.isolated.remove_takeprofit(
            RemoveTakeprofitParams(id=TRADE_ID)
        )

    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "DELETE"
    assert request.url.path == "/v3/futures/isolated/trade/takeprofit"
    assert request.url.params["id"] == TRADE_ID
    assert request.read() == b""
