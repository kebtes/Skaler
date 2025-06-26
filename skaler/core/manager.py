import httpx

from skaler import APIProvider, ProxyPool, Requester
from skaler.exceptions import NoAvailableProviders, RequestFailed


class SkaleManager:
    """
    Manages multiple API providers and optionally rotates through a proxy pool.
    Handles rate-limiting, provider blocking, and proxy rotation.

    Attributes:
        providers (List[APIProvider]): List of available API providers.
        requester (Requester): The HTTP client wrapper for sending requests.
        proxies (ProxyPool or None): Optional proxy pool for rotating proxies.
    """

    def __init__(self, providers: list[APIProvider], *, proxies: ProxyPool = None, requester=None):
        """
        Initializes the SkaleManager with providers, optional proxies, and a requester

        Args:
            providers (List[APIProvider]): List of API provider instances.
            proxies (ProxyPool, optional): ProxyPool instance to rotate proxies.
            requester (Requester, optional): Custom requester. Defaults to 'Requester()'.
        """

        self.providers = providers
        self.requester = requester or Requester()
        self.proxies = proxies or []

    async def send_request(self, method: str, url: str, headers=None, data=None, timeout=10) -> httpx.Response:
        """
        Sends an HTTP request using the first available provider.
        Will rotate through providers and proxies if necessary.

        Args:
            method (str): HTTP method (e.g., 'GET', 'POST').
            url (str): Target URL for the request.
            headers (dict, optional): Custom headers to include.
            data (dict, optional): JSON-serializable data to send in the request body.
            timeout (int): Timeout in seconds for the request.

        Returns:
            httpx.Response: The HTTP response from the API.

        Raises:
            RequestFailed: If the request fails due to a connection or API error.
            NoAvailableProviders: If all providers are blocked or rate-limited.
        """

        for provider in self.providers:
            if await provider.is_available():
                try:
                    headers = headers or {}
                    headers["Authorization"] = f"Bearer {provider.key}"
                    proxy = self.proxies.get_next() if self.proxies else None
                    response = await self.requester.send(
                        method=method,
                        url=url,
                        headers=headers,
                        json=data,
                        proxy=proxy,
                        timeout=timeout
                    )

                    await provider.record_usage()
                    return response
                except Exception as e:
                    await provider.block()
                    raise RequestFailed(
                        provider_name=provider.name,
                    ) from e

        raise NoAvailableProviders

    async def _get_next_proxy(self):
        """
        Returns the next proxy in a round-robin fashion by cycling through the proxy list.

        This method removes the first proxy from the list and appends it to the end,
        effectively rotating the list so that each proxy is used in turn.

        Returns:
            str or None: The next proxy URL if the proxy list is not empty; otherwise, None.
        """

        if not self.proxies:
            return None
        proxy = self.proxies.pop(0)
        self.proxies.append(proxy)
        return proxy
