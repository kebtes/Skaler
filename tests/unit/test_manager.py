from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from skaler import APIProvider, ProxyPool, Requester, SkaleManager
from skaler.exceptions import NoAvailableProviders, RequestFailed


@pytest.mark.asyncio
async def test_send_request_success():
    """
    Test a successful request using an available provider.

    This test ensures:
    - The provider is marked as available.
    - The request is sent using the Requester.
    - The proxy pool is used to get a proxy.
    - Usage is recorded properly.
    """

    # Mock available provider
    provider = AsyncMock(spec=APIProvider)
    provider.is_available.return_value = True
    provider.key = "test-key"
    provider.name = "TestProvider"
    provider.record_usage = AsyncMock()
    provider.block = AsyncMock()

    # Mock proxy pool
    proxy_pool = MagicMock(spec=ProxyPool)
    proxy_pool.get_next.return_value = "http://fake-proxy"

    # Mock requester with a successful response
    fake_response = httpx.Response(200, text="OK")
    requester = AsyncMock(spec=Requester)
    requester.send.return_value = fake_response

    # SkaleManager with the mocks
    manager = SkaleManager(
        providers=[provider],
        proxies=proxy_pool,
        requester=requester
    )

    res = await manager.send_request(
        "GET",
        "https://example.com"
    )

    # Assertions
    assert res.status_code == 200
    provider.is_available.assert_awaited_once()
    provider.record_usage.assert_awaited_once()
    requester.send.assert_awaited_once_with(
        method="GET",
        url="https://example.com",
        headers={"Authorization": "Bearer test-key"},
        json=None,
        proxy="http://fake-proxy",
        timeout=10,
    )

@pytest.mark.asyncio
async def test_send_request_fails_and_blocks_provider():
    """
    Test request failure and provider blocking.

    This test simulates a scenario where:
    - A provider is available.
    - A request attempt fails (raises an exception).
    - The provider should be marked as blocked.
    - 'RequestFailed' should be raised
    """

    provider = AsyncMock(spec=APIProvider)
    provider.is_available.return_value = True
    provider.key= "bad-key"
    provider.name = "FailProvider"
    provider.record_usage = AsyncMock()
    provider.block = AsyncMock()

    requester = AsyncMock(spec=Requester)
    requester.send.side_effect = Exception("Connection failed")

    manager = SkaleManager(
        providers=[provider],
        requester=requester
    )

    with pytest.raises(RequestFailed):
        await manager.send_request(
            "GET",
            "https://example.com"
        )

    provider.block.assert_awaited_once()

@pytest.mark.asyncio
async def test_no_available_providers():
    """
    Test the scenario where no providers are available.

    This test checks that:
    - If all providers return 'False' for 'is_available()',
    - Then 'NoAvailableProviders' is raised.
    """

    provider = AsyncMock(spec=APIProvider)
    provider.is_available.return_value = False
    provider.name = "UnavailableProvider"

    manager = SkaleManager(
        providers=[provider],
        requester=AsyncMock()
    )

    with pytest.raises(NoAvailableProviders):
        await manager.send_request(
            "GET",
            "https://example.com"
        )
