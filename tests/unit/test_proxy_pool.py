import time

import pytest

from skaler import ProxyPool


@pytest.mark.asyncio
async def test_empty_proxy_list_returns_none():
    """
    Test that get_next() returns None when the proxy list is empty.
    """
    pool = ProxyPool([])
    assert pool.get_next() is None


@pytest.mark.asyncio
async def test_round_robin_rotation():
    """
    Test that get_next() cycles through the proxies in round-robin order.
    """
    proxies = ["proxy1", "proxy2", "proxy3"]
    pool = ProxyPool(proxies)

    assert pool.get_next() == "proxy1"
    assert pool.get_next() == "proxy2"
    assert pool.get_next() == "proxy3"
    assert pool.get_next() == "proxy1"  # Should wrap around


@pytest.mark.asyncio
async def test_blocking_and_skipping_proxy(monkeypatch):
    """
    Test that blocked proxies are skipped by get_next().
    """
    proxies = ["proxy1", "proxy2", "proxy3"]
    pool = ProxyPool(proxies)

    now = 1000.0
    monkeypatch.setattr(time, "time", lambda: now)
    pool.block("proxy2", ttl=60)

    # get_next should skip proxy2
    assert pool.get_next() == "proxy1"
    assert pool.get_next() == "proxy3"
    assert pool.get_next() == "proxy1"  # proxy2 remains blocked


@pytest.mark.asyncio
async def test_auto_unblock_after_ttl(monkeypatch):
    """
    Test that proxies are automatically unblocked after TTL expires.
    """
    proxies = ["proxy1", "proxy2"]
    pool = ProxyPool(proxies)

    now = 1000.0
    monkeypatch.setattr(time, "time", lambda: now)
    pool.block("proxy1", ttl=60)

    # At current time, proxy1 is blocked, so get_next returns proxy2
    assert pool.get_next() == "proxy2"
    assert pool.get_next() == "proxy2"  # Still blocked, no proxy1

    # Advance time beyond TTL
    monkeypatch.setattr(time, "time", lambda: now + 61)

    # proxy1 should now be unblocked and returned
    assert pool.get_next() == "proxy1"
    assert pool.get_next() == "proxy2"


@pytest.mark.asyncio
async def test_get_next_returns_none_when_all_blocked(monkeypatch):
    """
    Test that get_next() returns None if all proxies are blocked.
    """
    proxies = ["proxy1", "proxy2"]
    pool = ProxyPool(proxies)

    now = 1000.0
    monkeypatch.setattr(time, "time", lambda: now)

    pool.block("proxy1", ttl=60)
    pool.block("proxy2", ttl=60)

    assert pool.get_next() is None
