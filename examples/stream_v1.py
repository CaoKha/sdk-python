"""Stream-v1 runnable example — exercises every public RPC + every topic listener.

RPC methods covered: hello, ping, time, authenticate, whoami,
                     subscribe, unsubscribe, unsubscribe_all.

Run (public-only, mainnet):
    uv run examples/stream_v1.py

Authenticated run reads creds by network:
    mainnet  -> MAINNET_API_KEY, MAINNET_API_KEY_SECRET, MAINNET_API_KEY_PASSPHRASE
    testnet4 -> TESTNET4_API_KEY, TESTNET4_API_KEY_SECRET, TESTNET4_API_KEY_PASSPHRASE

Creds loaded from `.env` via `python-dotenv`:
    uv run examples/stream_v1.py --auth

Defaults to mainnet. Pass --testnet4 to opt in:
    uv run examples/stream_v1.py --testnet4
    uv run examples/stream_v1.py --testnet4 --auth
"""

from __future__ import annotations

import asyncio
import contextlib
import os
import signal
import sys
from typing import Any

from dotenv import load_dotenv

from lnmarkets_sdk.stream.v1 import (
    StreamClientConfig,
    create_stream_client,
)
from lnmarkets_sdk.stream.v1.models import (
    AuthenticateParams,
    HelloParams,
    SubscribeParams,
    Topic,
    UnsubscribeParams,
)

load_dotenv()


def resolve_creds(network: str) -> tuple[str, str, str]:
    if network == "testnet4":
        key_var, secret_var, pass_var = (
            "TESTNET4_API_KEY",
            "TESTNET4_API_KEY_SECRET",
            "TESTNET4_API_KEY_PASSPHRASE",
        )
    else:
        key_var, secret_var, pass_var = (
            "MAINNET_API_KEY",
            "MAINNET_API_KEY_SECRET",
            "MAINNET_API_KEY_PASSPHRASE",
        )
    key = os.environ.get(key_var)
    secret = os.environ.get(secret_var)
    passphrase = os.environ.get(pass_var)
    if not key or not secret or not passphrase:
        print(
            f"--auth requires {key_var}, {secret_var}, {pass_var} env vars "
            f"(network={network})",
            file=sys.stderr,
        )
        sys.exit(1)
    return key, secret, passphrase


async def main() -> None:
    network = "mainnet" if "--mainnet" in sys.argv else "testnet4"
    want_auth = "--auth" in sys.argv

    if want_auth:
        resolve_creds(network)

    config = StreamClientConfig(
        network=network,
        reconnect_interval=5.0,
        reconnect_enabled=True,
        max_reconnect_attempts=5,
    )
    client = create_stream_client(config)

    # ---------------------------------------------------------------------
    # Lifecycle listeners
    # ---------------------------------------------------------------------

    client.on("open", lambda: print(f"[open] connected to {network}"))
    client.on(
        "close",
        lambda code, reason: print(f"[close] code={code} reason={reason or '(empty)'}"),
    )
    client.on("error", lambda err: print(f"[error] {err}", file=sys.stderr))
    client.on(
        "reconnected",
        lambda event: print(
            f"[reconnected] after {event['attempts']} attempt(s) "
            "— replay subscriptions here"
        ),
    )

    # ---------------------------------------------------------------------
    # Public topic listeners
    # ---------------------------------------------------------------------

    def handle_announcements(event: dict[str, Any]) -> None:
        if "title" in event:
            print(
                f"[announcements] ADD id={event.get('id')} title={event.get('title')}"
            )
        else:
            print(f"[announcements] REMOVE id={event.get('id')}")

    client.on("announcements", handle_announcements)

    client.on(
        "futures/inverse/btc_usd/ticker",
        lambda data: print(
            f"[ticker] time={data.get('time')} "
            f"lastPrice={data.get('lastPrice')} "
            f"fundingRate={data.get('funding', {}).get('rate'):.6f}"
        ),
    )
    client.on(
        "futures/inverse/btc_usd/lastPrice",
        lambda data: print(
            f"[lastPrice] time={data.get('time')} lastPrice={data.get('lastPrice')}"
        ),
    )
    client.on(
        "futures/inverse/btc_usd/index",
        lambda data: print(
            f"[index] time={data.get('time')} index={data.get('index')}"
        ),
    )
    client.on(
        "futures/inverse/btc_usd/buckets",
        lambda data: print(
            f"[buckets] time={data.get('time')} count={len(data.get('buckets', []))}"
        ),
    )
    client.on(
        "futures/inverse/btc_usd/funding",
        lambda data: print(
            f"[funding] pair={data.get('pair')} "
            f"rate={data.get('current', {}).get('rate'):.6f} "
            f"time={data.get('current', {}).get('time')}"
        ),
    )
    client.on(
        "futures/inverse/btc_usd/ohlc/1m",
        lambda candle: print(
            f"[ohlc/1m] o={candle.get('open')} h={candle.get('high')} "
            f"l={candle.get('low')} c={candle.get('close')} v={candle.get('volume')}"
        ),
    )
    client.on(
        "futures/inverse/btc_usd/ohlc/5m",
        lambda candle: print(
            f"[ohlc/5m] o={candle.get('open')} h={candle.get('high')} "
            f"l={candle.get('low')} c={candle.get('close')} v={candle.get('volume')}"
        ),
    )

    # ---------------------------------------------------------------------
    # Private topic listeners (only useful when authenticated)
    # ---------------------------------------------------------------------

    if want_auth:

        def handle_isolated_trades(event: dict[str, Any]) -> None:
            kind = event.get("event")
            trade = event.get("trade", {})
            if kind in ("open", "filled"):
                print(
                    f"[isolated/trades] {kind.upper()} id={trade.get('id')} "
                    f"price={trade.get('price')}"
                )
            elif kind == "canceled":
                print(f"[isolated/trades] CANCELED id={trade.get('id')}")
            elif kind == "liquidation":
                print(
                    f"[isolated/trades] LIQUIDATION id={trade.get('id')} "
                    f"exitPrice={trade.get('exitPrice')}"
                )
            elif kind == "funding":
                print(
                    f"[isolated/trades] FUNDING id={trade.get('id')} "
                    f"fundingFee={trade.get('fundingFee')}"
                )
            else:
                # closed | stoploss | takeprofit — same trade shape with pl + exitPrice
                print(
                    f"[isolated/trades] {str(kind).upper()} id={trade.get('id')} "
                    f"pl={trade.get('pl')} exitPrice={trade.get('exitPrice')}"
                )

        client.on("futures/inverse/btc_usd/isolated/trades", handle_isolated_trades)

        client.on(
            "wallet/deposit",
            lambda deposit: print(
                f"[wallet/deposit] id={deposit.get('id')} "
                f"amount={deposit.get('amount')} status={deposit.get('status')} "
                f"network={deposit.get('network')}"
            ),
        )

        client.on(
            "wallet/withdrawal",
            lambda withdrawal: print(
                f"[wallet/withdrawal] id={withdrawal.get('id')} "
                f"amount={withdrawal.get('amount')} fee={withdrawal.get('fee')} "
                f"status={withdrawal.get('status')}"
            ),
        )

        client.on(
            "futures/inverse/btc_usd/cross/orders",
            lambda event: print(
                f"[cross/orders] event={event.get('event')} "
                f"id={event.get('order', {}).get('id')} "
                f"side={event.get('order', {}).get('side')} "
                f"price={event.get('order', {}).get('price')}"
            ),
        )

        client.on(
            "futures/inverse/btc_usd/cross/position",
            lambda event: print(
                f"[cross/position] event={event.get('event')} "
                f"qty={event.get('position', {}).get('quantity')} "
                f"margin={event.get('position', {}).get('margin')} "
                f"pl={event.get('position', {}).get('totalPl')}"
            ),
        )

    # ---------------------------------------------------------------------
    # Connect + exercise every RPC method
    # ---------------------------------------------------------------------

    # Server rate-limits to 10 messages/sec per socket. Pace RPCs with a small
    # sleep so back-to-back calls stay comfortably under the ceiling.
    rpc_pace_s = 0.15

    await client.connect()

    hello = await client.public.hello(
        HelloParams(client_name="sdk-python-example", client_version="0.0.0"),
    )
    print(f"[rpc] hello -> version={hello.version}")
    await asyncio.sleep(rpc_pace_s)

    ping = await client.public.ping()
    print(f"[rpc] ping -> {ping}")
    await asyncio.sleep(rpc_pace_s)

    time = await client.public.time()
    print(f"[rpc] time -> {time.time}")
    await asyncio.sleep(rpc_pace_s)

    public_topics: list[Topic] = [
        "announcements",
        "futures/inverse/btc_usd/ticker",
        "futures/inverse/btc_usd/lastPrice",
        "futures/inverse/btc_usd/index",
        "futures/inverse/btc_usd/buckets",
        "futures/inverse/btc_usd/funding",
        "futures/inverse/btc_usd/ohlc/1m",
        "futures/inverse/btc_usd/ohlc/5m",
    ]

    if want_auth:
        key, secret, passphrase = resolve_creds(network)
        auth = await client.auth.authenticate(
            AuthenticateParams(key=key, secret=secret, passphrase=passphrase),
        )
        print(
            f"[rpc] authenticate -> authenticated={auth.authenticated} "
            f"permissions={len(auth.permissions)}"
        )
        await asyncio.sleep(rpc_pace_s)

        me = await client.auth.whoami()
        print(f"[rpc] whoami -> apiKey={me.api_key} userId={me.user_id}")
        await asyncio.sleep(rpc_pace_s)

        auth_topics: list[Topic] = [
            *public_topics,
            "wallet/deposit",
            "wallet/withdrawal",
            "futures/inverse/btc_usd/isolated/trades",
            "futures/inverse/btc_usd/cross/orders",
            "futures/inverse/btc_usd/cross/position",
        ]
        subscribed = await client.subscription.subscribe(
            SubscribeParams(topics=auth_topics),
        )
        print(f"[rpc] subscribe -> {', '.join(subscribed.subscribed)}")
        await asyncio.sleep(rpc_pace_s)

        # Demo single-topic unsubscribe — drop announcements only, rest keep streaming.
        dropped = await client.subscription.unsubscribe(
            UnsubscribeParams(topics=["announcements"]),
        )
    else:
        subscribed = await client.subscription.subscribe(
            SubscribeParams(topics=public_topics),
        )
        print(f"[rpc] subscribe -> {', '.join(subscribed.subscribed)}")
        await asyncio.sleep(rpc_pace_s)

        # Demo single-topic unsubscribe on public stream too.
        dropped = await client.subscription.unsubscribe(
            UnsubscribeParams(topics=["futures/inverse/btc_usd/ohlc/5m"]),
        )
    print(f"[rpc] unsubscribe -> {', '.join(dropped.unsubscribed)}")

    run_ms = int(os.environ.get("STREAM_V1_RUN_MS", "30000"))
    print(f"[run] streaming for {run_ms}ms — Ctrl+C to stop early")

    stop = asyncio.Event()

    async def shutdown(reason: str) -> None:
        print(f"[shutdown] {reason}")
        try:
            all_dropped = await client.subscription.unsubscribe_all()
            print(f"[rpc] unsubscribeAll -> {len(all_dropped.unsubscribed)} topic(s)")
        except Exception as error:  # noqa: BLE001
            print(f"[shutdown] unsubscribeAll failed: {error}", file=sys.stderr)
        await client.close()
        stop.set()

    loop = asyncio.get_running_loop()
    # Windows: signal handlers via add_signal_handler not supported.
    with contextlib.suppress(NotImplementedError):
        loop.add_signal_handler(
            signal.SIGINT,
            lambda: asyncio.create_task(shutdown("SIGINT")),
        )

    try:
        await asyncio.wait_for(stop.wait(), timeout=run_ms / 1000)
    except TimeoutError:
        await shutdown("timeout")


if __name__ == "__main__":
    asyncio.run(main())
