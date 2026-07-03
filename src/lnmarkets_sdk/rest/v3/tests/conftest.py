"""Shared pytest configuration for v3 integration tests."""

import pytest

from lnmarkets_sdk.rest.v3._internal.models import APIException


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item: pytest.Item):
    """Skip tests when the testnet trading engine is temporarily unavailable.

    Integration tests run against a live testnet; a 503 SERVICE_UNAVAILABLE
    from the trading engine is external flakiness, not an SDK failure.
    """
    try:
        return (yield)
    except APIException as exc:
        if exc.error is not None and exc.error.code == "SERVICE_UNAVAILABLE":
            pytest.skip(f"Trading engine unavailable on testnet: {exc}")
        raise
