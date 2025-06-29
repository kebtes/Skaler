import time


class InMemoryBackend:
    """
    A simple in-memory backedn for tracking API provider usage and block status.

    This backend can be used to enforce per-minute rate limits and temporarily
    block providers that have failed or exceeded their usage limits.

    Attributes:
        usage (dict): Tracks the number of requests per provider.
        blocked (dict): Tracks blocked providers and their unblock timestamps.
    """
    def __init__(self) -> None:
        """
        Initializes the in-memory data structure for usage and block tracking.
        """
        self.usage = {}
        self.blocked = {}

    async def increment_usage(self, provider_name: str) -> None:
        """
        Increments the usage count for a specific provider.

        Args:
            provider_name (str): The name of the provider.
        """
        self.usage[provider_name] = self.usage.get(provider_name, 0) + 1

    async def get_usage(self, provider_name: str) -> int:
        """
        Returns the current usage count for a specific provider.

        Args:
            provider_name (str): The name of the provider.

        Returns:
            int: The number of recorded requests.
        """
        return self.usage.get(provider_name, 0)

    async def reset_usage(self, provider_name: str) -> None:
        """
        Resets the usage count for a specific provider.

        Args:
            provider_name (str): The name of the provider.
        """
        if provider_name in self.usage:
            del self.usage[provider_name]

    async def block_provider(self, provider_name: str, ttl: int = 60):
        """
        Temporarily blocks a provider by storing its unblock timestamp.

        Args:
            provider_name (str): The name of the provider.
            ttl (int): Time in seconds to block the provider (default is 60).
        """
        unblock_time = time.time() + ttl
        self.blocked[provider_name] = unblock_time

    async def is_provider_blocked(self, provider_name: str) -> bool:
        """
        Checks if a provider is currently blocked. Automatically unblocks
        the provider if the TTL has expired.

        Args:
            provider_name (str): The name of the provider.

        Returns:
            bool: True if the provider is blocked, False otherwise.
        """
        unblock_time = self.blocked.get(provider_name)
        if unblock_time is None:
            return False
        if time.time() > unblock_time:
            del self.blocked[provider_name]
            return False
        return True
