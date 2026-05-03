import logging
import redis.asyncio as redis


class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.redis = None

    @property
    def _redis(self):
        assert self.redis is not None, "Redis не подключен"
        return self.redis

    async def connection(self):
        logging.info(f"Начинаю подключение к редис host={self.host}, port={self.port}")
        self.redis = redis.Redis(host=self.host, port=self.port)
        logging.info(f"Успешно подключился к редис host={self.host}, port={self.port}")

    async def set(self, key: str, value: str, expire: int | None = None):
        if expire:
            await self._redis.set(key, value, ex=expire)
        else:
            await self._redis.set(key, value)

    async def get(self, key: str):
        return await self._redis.get(key)

    async def delete(self, key: str):
        await self._redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
