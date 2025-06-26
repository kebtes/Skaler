
import aioreddis


class RedisBackend:
    def __init__(self, redis_url="redis://localhost"):
        self.redis = aioreddis.from_url(redis_url, decode_responses=True)

    async def increment_usage(self, provider_name: str):
        key = f"provider:{provider_name}:usage"
        await self.redis.incr(key)

    async def get_usage(self, provider_name: str) -> int:
        key = f"provider:{provider_name}:usage"
        return int(await self.redis.get(key) or 0)

    async def reset_usage(self, provider_name: str):
        key = f"provider:{provider_name}:usage"
        await self.redis.delete(key)
