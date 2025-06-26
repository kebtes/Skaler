import httpx


class Requester:
    """
    A simple asynchronous HTTP client wrapper using httpx.AsyncClient.
    Supports optional proxying and custom headers.

    Designed to be used internally by SkaleManager for sending API requests
    with optional proxy rotation and error handling.
    """

    def __init__(self):
        """
        Initializes the async HTTP client.
        """
        self.client = httpx.AsyncClient()

    async def send(self, method: str, url: str, headers=None, json=None, proxy=None, timeout=10):
        """
        Sends an asynchronous HTTP request with optional proxy and headers.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST').
            url (str): The full target URL of the request.
            headers (dict, optional): Optional HTTP headers to include.
            json (dict, optional): JSON-serializable payload for the request body.
            proxy (str, optional): Proxy URL to route the request through.
            timeout (int, optional): Request timeout in seconds. Default is 10.

        Returns:
            httpx.Response: The response object from the request.

        Raises:
            httpx.RequestError: If the request fails (e.g., timeout, connection error)
        """

        return await self.client.request(
            method=method,
            url=url,
            headers=headers,
            json=json,
            timeout=timeout,
            proxies={"http": proxy, "https": proxy} if proxy else None
        )
