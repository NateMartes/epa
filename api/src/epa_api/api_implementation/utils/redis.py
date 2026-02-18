from json.decoder import JSONDecodeError
from typing import Any, Dict
import redis.asyncio 
import os
import json

class RedisUtils:
    """A class with helpful methods to interact with Redis"""

    @staticmethod
    def get_redis_connection() -> redis.asyncio.Redis:
        """
        Gets a connection to the underlying redis instance.
        
        :return: A instance to a redis database
        :rtype: redis.asyncio.Redis
        """
        hostname = os.getenv("EPA_REDIS_HOSTNAME")
        port = os.getenv("EPA_REDIS_PORT")
        password = os.getenv("EPA_REDIS_PASSWORD")
        if not hostname or not port or not password:
            raise ValueError("Not all redis environment variables are set")
        
        try:
            port = int(port)
        except TypeError:
            raise TypeError("EPA_REDIS_PORT must be a integer")
            
        return redis.asyncio.Redis(host=hostname, port=port, db=0, password=password)
        

    @staticmethod
    async def get_user_subscribed_posts(rdb: redis.asyncio.Redis, user_id: str) -> list | None:
        """
        Gets a user's subscribed posts from their cache line.
        
        :param rdb: A instance of the redis database connection
        :type rdb: redis.asyncio.Redis
        :param user_id: The id of the user to get the posts for
        :type user_id: str
        :return: A list of raw post objects, or None if no posts exists
        :rtype: list | None
        """
        posts = await rdb.get(user_id)
        if posts:
            try:
                posts = json.loads(posts)
            except JSONDecodeError as e:
                raise e
                
        return posts
        
    @staticmethod
    async def clear_user_subscribed_posts(rdb: redis.asyncio.Redis, user_id: str):
        """
        Removes a user's subscribed posts from the cache
        
        :param rdb: A instance of the redis database connection
        :type rdb: redis.asyncio.Redis
        :param user_id: The id of the user to get the posts for
        :type user_id: str
        """
        await rdb.delete(user_id)
        
    @staticmethod
    async def close(rdb: redis.asyncio.Redis):
        """
        Closes a connection to a redis instance
        
        :param rdb: A instance of the redis database connection
        :type rdb: redis.asyncio.Redis
        """
        await rdb.close()
        