from epa_api.api_implementation.utils.redis import RedisUtils
import redis.asyncio

class CacheUtils:
    """A class with helpful methods to interact with cached items"""
    
    @staticmethod
    async def get_user_subscribed_posts(rdb: redis.asyncio.Redis, user_id: str) -> list | None:
        return await RedisUtils.get_user_subscribed_posts(rdb, user_id)
        
    @staticmethod
    async def clear_user_subscribed_posts(rdb: redis.asyncio.Redis, user_id: str):
        return await RedisUtils.clear_user_subscribed_posts(rdb, user_id)