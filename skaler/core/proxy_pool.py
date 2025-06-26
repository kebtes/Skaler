import time


class ProxyPool:
    """
    Manages a list of proxies with round-robin rotation and temporary blocking.
    Automatically skips over proxies that are blocked and re-includes them after TTL.

    Attributes:
        _proxies (List[str]): List of proxy URLS.
        _index (int): Current index in the proxy list for round-robin rotation.
        _blocked (Dict[str, float]): Dictionary mapping proxy URLs to unblock timestamps.
    """

    def __init__(self, proxy_list: list[str]):
        """
        Initializes the proxy pool with a list of proxies.

        Args:
            proxy_list (List[str]): A list of proxy URLs.
        """

        self._proxies = proxy_list
        self._index = 0
        self._blocked = {} # proxy_url -> unblock_time

    def get_next(self) -> str | None:
        """
        Returns the next available (not blocked) proxy using round-robin rotation.

        Returns:
            str | None: The next available proxy URL, or None if all are blocked or list is empty.
        """
        start = self._index

        if not self._proxies:
            return None

        while True:
            proxy = self._proxies[self._index]
            self._index = (self._index + 1) % len(self._proxies)

            if not self._is_blocked(proxy):
                return proxy

            if self._index == start:
                return None

    def block(self, proxy: str, ttl: int = 60):
        """
        Temporarily blocks a proxy for a given number of seconds.

        Args:
            proxy (str): The proxy URL to block.
            ttl (int): Time-to-live (in seconds) before the proxy becomes available again.
        """

        self._blocked[proxy] = time.time() + ttl

    def _is_blocked(self, proxy: str) -> bool:
        """
        Checks whether a proxy is currently blocked. Unblocks it if TTL has expired.

        Args:
            proxy (str): The proxy URL to check.

        Returns:
            bool: True if the proxy is still blocked, False otherwise.
        """
        unblock_time = self._blocked.get(proxy)
        if not unblock_time:
            return False

        if time.time() > unblock_time:
            del self._blocked[proxy] # Auto-unblock
            return False
        return True
