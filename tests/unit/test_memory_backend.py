import time

import pytest

from skaler.backend import InMemoryBackend


@pytest.mark.asyncio
async def test_increment_and_get_usage():
    """
    Test that usage increments properly and get_usage returns correct counts.
    """
    backend = InMemoryBackend()

    await backend.increment_usage("provider1")
    await backend.increment_usage("provider1")

    usage = await backend.get_usage("provider1")
    assert usage == 2

    # Unused provider returns 0
    usage = await backend.get_usage("provider2")
    assert usage == 0


@pytest.mark.asyncio
async def test_reset_usage():
    """
    Test that reset_usage properly clears the usage count for a provider.
    """
    backend = InMemoryBackend()
    await backend.increment_usage("provider1")
    usage_before = await backend.get_usage("provider1")
    assert usage_before == 1

    await backend.reset_usage("provider1")
    usage_after = await backend.get_usage("provider1")
    assert usage_after == 0


@pytest.mark.asyncio
async def test_block_and_check_block_status(monkeypatch):
    """
    Test that blocking a provider sets the unblock time,
    and is_provider_blocked correctly reports block status.
    """
    backend = InMemoryBackend()

    now = 1000.0
    monkeypatch.setattr(time, "time", lambda: now)

    await backend.block_provider("provider1", ttl=60)

    # Immediately after blocking, provider should be blocked
    is_blocked = await backend.is_provider_blocked("provider1")
    assert is_blocked is True

    # Advance time beyond TTL
    monkeypatch.setattr(time, "time", lambda: now + 61)

    # After TTL expires, provider should not be blocked
    is_blocked = await backend.is_provider_blocked("provider1")
    assert is_blocked is False

    # Block info should be removed after TTL expires
    assert "provider1" not in backend.blocked


@pytest.mark.asyncio
async def test_is_provider_blocked_returns_false_if_not_blocked():
    """
    Test that is_provider_blocked returns False for providers never blocked.
    """
    backend = InMemoryBackend()
    blocked = await backend.is_provider_blocked("unknown_provider")
    assert blocked is False
