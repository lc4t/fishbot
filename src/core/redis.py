import os

import aioredis


class Redis:
    redis_pool = None

    def __init__(self, app):
        self.app = app

    async def get(self):
        REDIS_CONFIG = {
            'address': (os.getenv('REDIS_HOST'), os.getenv('REDIS_PORT')),
            'password': os.getenv('REDIS_PASSWORD', ''),
            'db': os.getenv('REDIS_DB', 0),
            'minsize': os.getenv('REDIS_MINSIZE', 1),
            'maxsize': os.getenv('REDIS_MAXSIZE', 10),
            'encoding': 'utf-8',
        }

        if not self.redis_pool:
            self.redis_pool = await aioredis.create_redis_pool(**REDIS_CONFIG)
        return self.redis_pool

    async def close(self):
        if self.redis_pool:
            self.redis_pool.close()
            await self.redis_pool.wait_closed()
