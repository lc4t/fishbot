import datetime

from init import app
from loguru import logger
from hashlib import sha512

ip = None


# async def get_out_ip(app):
async def get_out_ip():
    global ip
    if not ip:
        async with app.ctx.aiohttp_session.get('https://checkip.amazonaws.com') as resp:
            ip = await resp.text()
            logger.info(f'IP: {ip}')
    return ip


async def calc_hash(*args):
    s = ''
    for arg in args:
        if isinstance(arg, dict):
            for k in sorted(arg):
                s += f'{k}={arg.get(k)}'
        elif isinstance(arg, list):
            for i in arg:
                s += await calc_hash(i)
        elif isinstance(arg, str):
            s += f'{arg}'
    return sha512(s.encode()).hexdigest()
