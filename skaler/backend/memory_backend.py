import time


class InMemoryBackend:
    def __init__(self):
        self.usage = {}
        self.blocked = {}

    async def increment_usage(self, provider_name: str):
        self.usage[provider_name] = self.usage.get(provider_name, 0) + 1

    async def get_usage(self, provider_name: str) -> int:
        return self.usage.get(provider_name, 0)

    async def reset_usage(self, provider_name: str):
        if provider_name in self.usage:
            del self.usage[provider_name]

    async def block_provider(self, provider_name: str) -> bool:
        unblock_time = self.blocked.get(provider_name)
        if unblock_time is None:
            return False
        if time.time() > unblock_time:
            del self.blocked[provider_name]
            return False
        return True
