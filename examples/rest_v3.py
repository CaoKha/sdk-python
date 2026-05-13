"""REST v3 runnable example — public endpoints + optional authenticated flow.

Creds loaded from `.env` via `python-dotenv`.

Run:
    uv run examples/rest_v3.py                  # public-only, testnet4
    uv run examples/rest_v3.py --auth           # authenticated, testnet4
    uv run examples/rest_v3.py --mainnet
    uv run examples/rest_v3.py --mainnet --auth

Authenticated run reads creds by network:
    mainnet  -> MAINNET_API_KEY, MAINNET_API_KEY_SECRET, MAINNET_API_KEY_PASSPHRASE
    testnet4 -> TESTNET4_API_KEY, TESTNET4_API_KEY_SECRET, TESTNET4_API_KEY_PASSPHRASE
"""

import asyncio
import os
import sys
from pprint import pprint
from typing import Literal

from dotenv import load_dotenv

from lnmarkets_sdk.rest.v3.http.client import APIAuthContext, APIClientConfig, LNMClient
from lnmarkets_sdk.rest.v3.models.account import (
    GetLightningDepositsParams,
    GetNotificationsParams,
)
from lnmarkets_sdk.rest.v3.models.futures_cross import FuturesCrossOrderLimit
from lnmarkets_sdk.rest.v3.models.futures_data import (
    GetCandlesParams,
    GetFundingSettlementsParams,
)
from lnmarkets_sdk.rest.v3.models.futures_isolated import (
    CloseTradeParams,
    FuturesOrder,
    GetClosedTradesParams,
    GetIsolatedFundingFeesParams,
    UpdateTakeprofitParams,
)
from lnmarkets_sdk.rest.v3.models.oracle import GetLastPriceParams

Network = Literal["mainnet", "testnet4"]

load_dotenv()


async def example_public_endpoints(network: Network):
    """Example: Make public requests without authentication."""
    print("\n" + "=" * 80)
    print(f"PUBLIC ENDPOINTS EXAMPLE ({network})")
    print("=" * 80)

    # Create client without authentication for public endpoints
    # The httpx.AsyncClient is created once and reuses connections
    async with LNMClient(APIClientConfig(network=network)) as client:
        # All these requests share the same connection pool
        print("\n🔄 Making multiple requests with connection reuse...")

        # Get futures ticker
        ticker = await client.futures.get_ticker()
        print("\n--- Futures Ticker ---")
        pprint(ticker.model_dump(), indent=2, width=100)

        # Get leaderboard
        await asyncio.sleep(1)
        leaderboard = await client.futures.get_leaderboard()
        print("\n--- Leaderboard (Top 3 Daily) ---")
        pprint(leaderboard.daily[:3], indent=2, width=100)

        # Get oracle data
        await asyncio.sleep(1)
        oracle_index = await client.oracle.get_index()
        print("\n--- Oracle Index (Latest) ---")
        pprint(oracle_index[0].model_dump() if oracle_index else "No data", indent=2)

        # Get synthetic USD best price
        await asyncio.sleep(1)
        best_price = await client.synthetic_usd.get_best_price()
        print("\n--- Synthetic USD Best Price ---")
        pprint(best_price.model_dump(), indent=2)

        # Ping the API
        await asyncio.sleep(1)
        ping_response = await client.ping()
        print("\n--- Ping ---")
        print(f"Response: {ping_response}")

        # Get server time
        await asyncio.sleep(1)
        time_response = await client.time()
        print("\n--- Server Time ---")
        print(f"Response: {time_response}")

        # Get futures candles
        await asyncio.sleep(1)
        candles_params = GetCandlesParams(
            from_="2024-01-01T00:00:00.000Z",
            range="1h",
            limit=5,
        )
        candles = await client.futures.get_candles(candles_params)
        print("\n--- Futures Candles (Last 5) ---")
        for candle in candles.data[:3]:  # Show first 3
            print(
                f"Time: {candle.time}, OHLC: {candle.open}/{candle.high}/{candle.low}/{candle.close}"
            )

        # Get funding settlements
        await asyncio.sleep(1)
        funding_settlements = await client.futures.get_funding_settlements(
            GetFundingSettlementsParams(limit=5)
        )
        print("\n--- Funding Settlements (Last 5) ---")
        for settlement in funding_settlements.data[:3]:  # Show first 3
            print(
                f"Rate: {settlement.funding_rate}, Price: {settlement.fixing_price}, Time: {settlement.time}"
            )

        # Get oracle last price
        await asyncio.sleep(1)
        last_prices = await client.oracle.get_last_price(GetLastPriceParams(limit=5))
        print("\n--- Oracle Last Price (Last 5) ---")
        for price in last_prices[:3]:  # Show first 3
            print(f"Price: {price.last_price}, Time: {price.time}")


async def example_authenticated_endpoints(network: Network):
    """Example: Use authenticated endpoints with credentials."""
    print("\n" + "=" * 80)
    print(f"AUTHENTICATED ENDPOINTS EXAMPLE ({network})")
    print("=" * 80)

    prefix = network.upper()
    key = os.getenv(f"{prefix}_API_KEY")
    secret = os.getenv(f"{prefix}_API_KEY_SECRET")
    passphrase = os.getenv(f"{prefix}_API_KEY_PASSPHRASE")

    if not (key and secret and passphrase):
        print("\n⚠️  Skipping authenticated example:")
        print(
            f"    Please set {prefix}_API_KEY, {prefix}_API_KEY_SECRET, "
            f"and {prefix}_API_KEY_PASSPHRASE"
        )
        return

    # Create config with authentication and custom timeout
    config = APIClientConfig(
        authentication=APIAuthContext(
            key=key,
            secret=secret,
            passphrase=passphrase,
        ),
        network=network,
        timeout=60.0,  # 60 second timeout (default is 30s)
    )

    async with LNMClient(config) as client:
        print("\n🔐 Using authenticated endpoints with connection pooling...")

        # Get account info
        account = await client.account.get_account()
        print("\n--- Account Info ---")
        print(f"Username: {account.username}")
        print(f"Balance: {account.balance} sats")
        print(f"Synthetic USD Balance: {account.synthetic_usd_balance}")

        # Get Bitcoin address
        btc_address = await client.account.get_bitcoin_address()
        print("\n--- Bitcoin Deposit Address ---")
        print(f"Address: {btc_address.address}")

        # Get lightning deposits (last 5)
        deposits_response = await client.account.get_lightning_deposits(
            GetLightningDepositsParams(from_="1970-01-01T00:00:00.000Z", limit=5)
        )
        print(
            f"\n--- Recent Lightning Deposits (Last {len(deposits_response.data)}) ---"
        )
        for deposit in deposits_response.data:
            print(f"Deposits {deposit.amount} sats at {deposit.created_at}")

        # List current notifications. Notifications fire server-side on async
        # events (deposit settled, withdrawal processed, trade closed by SL/TP,
        # funding settlements, system announcements) — not synchronously from
        # the client. List may be empty on a fresh testnet account.
        await asyncio.sleep(1)
        notifs = await client.account.get_notifications(GetNotificationsParams(limit=5))
        unread = sum(1 for n in notifs.data if not n.read)
        print(f"\n--- Notifications (unread: {unread}/{len(notifs.data)}) ---")
        for n in notifs.data[:3]:
            print(f"  [{'x' if n.read else ' '}] {n.message}")

        # Mark all notifications as read (no-op if list is empty)
        await asyncio.sleep(1)
        await client.account.read_notifications()
        print("\n--- read_notifications() called ---")

        # Get running trades
        await asyncio.sleep(1)
        running_trades = await client.futures.isolated.get_running_trades()
        print("\n--- Running Isolated Trades ---")
        print(f"Count: {len(running_trades)}")
        for trade in running_trades[:3]:  # Show first 3
            side = "LONG" if trade.side == "buy" else "SHORT"
            print(
                f"  {side} - Margin: {trade.margin} sats, Leverage: {trade.leverage}x, PL: {trade.pl} sats"
            )

        # Get open trades
        await asyncio.sleep(1)
        open_trades = await client.futures.isolated.get_open_trades()
        print(f"\n--- Open Isolated Trades (Count: {len(open_trades)}) ---")
        for trade in open_trades[:3]:  # Show first 3
            side = "LONG" if trade.side == "buy" else "SHORT"
            print(f"  {side} - Price: {trade.price}, Quantity: {trade.quantity}")

        # Get closed trades
        await asyncio.sleep(1)
        closed_trades = await client.futures.isolated.get_closed_trades(
            GetClosedTradesParams(limit=5)
        )
        print(f"\n--- Closed Isolated Trades (Last {len(closed_trades.data)}) ---")
        for trade in closed_trades.data[:3]:  # Show first 3
            side = "LONG" if trade.side == "buy" else "SHORT"
            print(f"  {side} - PL: {trade.pl} sats, Closed: {trade.closed}")

        # Get isolated funding fees
        await asyncio.sleep(1)
        isolated_fees = await client.futures.isolated.get_funding_fees(
            GetIsolatedFundingFeesParams(limit=5)
        )
        print(f"\n--- Isolated Funding Fees (Last {len(isolated_fees.data)}) ---")
        for fee in isolated_fees.data[:3]:  # Show first 3
            print(f"Fee: {fee.fee} sats, Time: {fee.time}")

        # Get cross margin position
        try:
            position = await client.futures.cross.get_position()
            print("\n--- Cross Margin Position ---")
            print(f"Quantity: {position.quantity}")
            print(f"Margin: {position.margin} sats")
            print(f"Leverage: {position.leverage}x")
            print(f"Total PL: {position.total_pl} sats")
        except Exception as e:
            print(f"Error: {e}")

        # Open a new cross order
        try:
            print("\n--- Try to open a new cross order ---")
            order_params = FuturesCrossOrderLimit(
                type="limit",
                price=101000,
                quantity=10,
                side="sell",
                client_id="custom-ref-123",
            )
            new_order = await client.futures.cross.new_order(order_params)
            print(f"New order: {new_order}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n --- Open isolated market trade then update take profit ---")
        try:
            new_trade_params = FuturesOrder(
                type="market",
                side="buy",
                quantity=1,
                leverage=10,
                takeprofit=150_000,
            )
            opened = await client.futures.isolated.new_trade(new_trade_params)
            print(f"Opened trade ID: {opened.id}, takeprofit: {opened.takeprofit}")

            await asyncio.sleep(1)
            tp_params = UpdateTakeprofitParams(id=opened.id, value=200_000)
            updated = await client.futures.isolated.update_takeprofit(tp_params)
            print(f"New take profit: {updated.takeprofit}")

            await asyncio.sleep(1)
            closed = await client.futures.isolated.close(CloseTradeParams(id=opened.id))
            print(f"Closed trade {closed.id} - PL: {closed.pl} sats")
        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Run all examples."""
    network: Network = "mainnet" if "--mainnet" in sys.argv else "testnet4"
    want_auth = "--auth" in sys.argv

    print("\n" + "=" * 80)
    print(f"LN MARKETS V3 CLIENT EXAMPLES (network={network}, auth={want_auth})")
    print("=" * 80)

    await example_public_endpoints(network)
    if want_auth:
        await example_authenticated_endpoints(network)

    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
