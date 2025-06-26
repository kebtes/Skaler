from skaler.backend import InMemoryBackend


class APIProvider:
    """
    Represents a single API key/provider in the Skaler system.
    Tracks usage, handles rate limiting, and integrates with a backend
    to manage usage state and blocking bahavior.

    Attributes:
        name (str): A unique identifier for this provider.
        key (str): The actual API key string to be used in requests.
        limit (int): The maximum number of requests allowed per minute.
        backedn (BaseBackend): Backend used for tracking usage and block state.
    """
    def __init__(self, name, key, limit_per_minute: int, backend=None):
        """
        Initializes a new API provider instance with a rate limit and optional backend.

        Args:
            name (str): Unique name for the provider.
            key (str): The API key string to be used in Authorization headers.
            limit_per_minute (int): Requests allowed per minute.
            backend (BaseBackend, optional): Custom backend. Defaults to InMemoryBackend.
        """
        self.name = name
        self.key = key
        self.limit = limit_per_minute
        self.backend = backend or InMemoryBackend()

    async def is_available(self) -> bool:
        """
        Checks if the provider is currently available for use.
        A provider is unavailable if it is blocked or has exceeded its rate limit.

        Returns:
            bool: True if available, False otherwise.
        """
        blocked = await self.backend.is_provider_blocked(self.name)
        usage = await self.backend.get_usage(self.name)
        return not blocked and usage < self.limit

    async def record_usage(self):
        """
        Increments the usage counter for this provider.
        Called after each successful request.
        """
        await self.backend.increment_usage(self.name)

    async def block(self, ttl: int = 60):
        """
        Blocks this provider for a set duration (TTL in seconds)

        Args:
            ttl (int): Time-to-live in seconds for the block duration. Default is 60 seconds.
        """
        await self.backend.block_provider(self.name, ttl)

    def __str__(self):
        """
        Returns the string representation of the provider (its name).

        Returns:
            str: The provider's name.
        """
        return self.name
