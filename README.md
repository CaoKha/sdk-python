# LN Markets SDK

[![CI](https://github.com/ln-markets/sdk-python/actions/workflows/check.yml/badge.svg)](https://github.com/ln-markets/sdk-python/actions/workflows/check.yml)

Python SDK for the LN Markets API. Ships two clients:

- **REST v3** (`lnmarkets_sdk.rest.v3`) — request/response API.
- **Stream v1** (`lnmarkets_sdk.stream.v1`) — JSON-RPC WebSocket with subscriptions.

## REST v3

For public endpoints, you can just do this:

```python
from lnmarkets_sdk.rest.v3.http.client import LNMClient
import asyncio

async with LNMClient() as client:
  ticker = await client.futures.get_ticker()
  await asyncio.sleep(1)
  leaderboard = await client.futures.get_leaderboard()
```

Remember to sleep between requests, as the rate limit is 1 requests per second for public endpoints.

For endpoints that need authentication, you need to create an instance of the `LNMClient` class and provide your API credentials:

```python
from lnmarkets_sdk.rest.v3.http.client import APIAuthContext, APIClientConfig, LNMClient

config = APIClientConfig(
    authentication=APIAuthContext(
        key=your_key,
        secret=your_secret,
        passphrase=your_passphrase,
    ),
    network="mainnet",
    timeout=60.0,  # 60 second timeout (default is 30s)
    )

async with LNMClient(config) as client:
  account = await client.account.get_account()
```

For endpoints that requires input parameters, you can find the corresponding models in the `lnmarkets_sdk.rest.v3.models` module.

```python

from lnmarkets_sdk.rest.v3.http.client import APIAuthContext, APIClientConfig, LNMClient
from lnmarkets_sdk.rest.v3.models.account import GetLightningDepositsParams

config = APIClientConfig(
    authentication=APIAuthContext(
        key=your_key,
        secret=your_secret,
        passphrase=your_passphrase,
    ),
    network="mainnet",
    timeout=60.0,  # 60 second timeout (default is 30s)
    )

async with LNMClient(config) as client:
    deposits = await client.account.get_lightning_deposits(
        GetLightningDepositsParams(limit=5)
    )
```

Check our [REST example](./examples/rest_v3.py) for more details.

### Available Methods

🔒 = requires API credentials

```python
# Ping
client.ping()

# Account 🔒
client.account.get_account()
client.account.get_bitcoin_address()
client.account.add_bitcoin_address()
client.account.deposit_lightning()
client.account.withdraw_lightning()
client.account.withdraw_on_chain()
client.account.get_lightning_deposits()
client.account.get_lightning_withdrawals()
client.account.get_on_chain_deposits()
client.account.get_on_chain_withdrawals()
client.account.read_notifications()

# Futures
client.futures.get_ticker()
client.futures.get_leaderboard()
client.futures.get_candles()
client.futures.get_funding_settlements()

# Futures Isolated 🔒
client.futures.isolated.new_trade()
client.futures.isolated.get_running_trades()
client.futures.isolated.get_open_trades()
client.futures.isolated.get_closed_trades()
client.futures.isolated.close()
client.futures.isolated.cancel()
client.futures.isolated.cancel_all()
client.futures.isolated.add_margin()
client.futures.isolated.cash_in()
client.futures.isolated.update_stoploss()
client.futures.isolated.update_takeprofit()
client.futures.isolated.get_funding_fees()

# Futures Cross 🔒
client.futures.cross.new_order()
client.futures.cross.get_position()
client.futures.cross.get_open_orders()
client.futures.cross.get_filled_orders()
client.futures.cross.close()
client.futures.cross.cancel()
client.futures.cross.cancel_all()
client.futures.cross.deposit()
client.futures.cross.withdraw()
client.futures.cross.set_leverage()
client.futures.cross.get_transfers()
client.futures.cross.get_funding_fees()

# Oracle
client.oracle.get_index()
client.oracle.get_last_price()

# Synthetic USD
client.synthetic_usd.get_best_price()
client.synthetic_usd.get_swaps()  # 🔒
client.synthetic_usd.new_swap()   # 🔒
```

## Stream v1

WebSocket JSON-RPC client. Connect, subscribe to topics, register event listeners.

Public stream:

```python
import asyncio
from lnmarkets_sdk.stream.v1 import StreamClientConfig, create_stream_client
from lnmarkets_sdk.stream.v1.models import SubscribeParams

async def main():
    config = StreamClientConfig(network="mainnet")
    client = create_stream_client(config)

    client.on(
        "futures/inverse/btc_usd/ticker",
        lambda data: print(data["lastPrice"]),
    )

    await client.connect()
    await client.subscription.subscribe(
        SubscribeParams(topics=["futures/inverse/btc_usd/ticker"]),
    )
    await asyncio.sleep(30)
    await client.close()

asyncio.run(main())
```

Authenticated stream (private topics: trades, orders, position, wallet):

```python
from lnmarkets_sdk.stream.v1 import StreamClientConfig, create_stream_client
from lnmarkets_sdk.stream.v1.models import AuthenticateParams, SubscribeParams

config = StreamClientConfig(
    network="mainnet",
    reconnect_enabled=True,
    reconnect_interval=5.0,
    max_reconnect_attempts=5,
)
client = create_stream_client(config)

await client.connect()
await client.auth.authenticate(
    AuthenticateParams(key=your_key, secret=your_secret, passphrase=your_passphrase),
)
await client.subscription.subscribe(
    SubscribeParams(topics=[
        "futures/inverse/btc_usd/isolated/trades",
        "wallet/deposit",
        "wallet/withdrawal",
    ]),
)
```

Server rate-limits to 10 messages/sec per socket — pace RPC calls accordingly.

Check our [Stream example](./examples/stream_v1.py) for full RPC + topic coverage.

### Available RPCs and Topics

🔒 = requires authentication

```python
# Public RPCs
client.public.hello()
client.public.ping()
client.public.time()

# Auth RPCs 🔒
client.auth.authenticate()
client.auth.whoami()

# Subscription RPCs
client.subscription.subscribe()
client.subscription.unsubscribe()
client.subscription.unsubscribe_all()

# Lifecycle events
client.on("open", ...)
client.on("close", ...)
client.on("error", ...)
client.on("reconnected", ...)

# Public topics
"announcements"
"futures/inverse/btc_usd/ticker"
"futures/inverse/btc_usd/lastPrice"
"futures/inverse/btc_usd/index"
"futures/inverse/btc_usd/buckets"
"futures/inverse/btc_usd/funding"
"futures/inverse/btc_usd/ohlc/1m"
"futures/inverse/btc_usd/ohlc/5m"

# Private topics 🔒
"futures/inverse/btc_usd/isolated/trades"
"futures/inverse/btc_usd/cross/orders"
"futures/inverse/btc_usd/cross/position"
"wallet/deposit"
"wallet/withdrawal"
```

## API Reference

- [REST](https://docs.lnmarkets.com/en/api)
- [STREAM](https://docs.lnmarkets.com/en/stream)

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
