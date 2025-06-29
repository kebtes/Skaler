class DummyProvider:
    """
    A minimal stub provider used when no actual API keys or rate-limiting
    are needed.

    This is useful for scenarios like web scraping where you only care about
    proxy-rotation and don't need to manage rate limits, usage, or blocking
    per provider.

    Attributes:
        name (str): The name of the provider, defaults to "dummy".
    """

    def __init__(self):
        """
        Initializes the dummy provider with a default name.
        """
        self.name = "dummy"

    async def is_available(self) -> bool:
        """
        Always returns True, since this provider is never blocked or
        rate-limited.

        Returns:
            bool: Always True.
        """
        return True

    async def record_usage(self):
        """
        No-op method for recording usage.
        Exists to satisfy the expected APIProvider interface.
        """
        pass

    async def block(self, ttl=60):
        """
        No-op method for blocking.
        Exists to satisfy the expected APIProvider interface.

        Args:
            ttl (int): Time to block, ignored in DummyProvider.
        """
        pass
