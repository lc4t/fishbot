# async def test(app):
#     rb = await app.ctx.aiohttp_session.get('http://httpbin.org/get')
#     rb = await rb.json()
#     logger.info(rb)
from loguru import logger
from init import app


class HTTP:
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    }

    def __init__(self, app):
        self.app = app

    async def get_json(self, url, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = self.default_headers
        async with app.ctx.aiohttp_sem:
            async with self.app.ctx.aiohttp_session.get(url, *args, **kwargs) as resp:
                if resp.status != 200:
                    logger.error(f'{resp.status} {url}')
                    return None
                return await resp.json()

    async def get_text(self, url, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = self.default_headers
        async with app.ctx.aiohttp_sem:
            async with self.app.ctx.aiohttp_session.get(url, *args, **kwargs) as resp:
                if resp.status != 200:
                    logger.error(f'{resp.status} {url}')
                    return None
                return await resp.text()

    async def post_json(self, url, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = self.default_headers
        async with app.ctx.aiohttp_sem:
            async with self.app.ctx.aiohttp_session.post(url, *args, **kwargs) as resp:
                if resp.status != 200:
                    logger.error(f'{resp.status} {url}')
                    return None
                return await resp.json()

    async def post_text(self, url, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = self.default_headers
        async with app.ctx.aiohttp_sem:
            async with self.app.ctx.aiohttp_session.post(url, *args, **kwargs) as resp:
                if resp.status != 200:
                    logger.error(f'{resp.status} {url}')
                    return None
                return await resp.text()
