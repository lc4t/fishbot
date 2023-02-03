from init import logger
from .bilibili import Bilibili


async def new_task(discover, *args, **kwargs):
    if discover.get('type').startswith('bilibili.'):
        return await Bilibili.new_task(discover, *args, **kwargs)
    else:
        logger.warning(f'unknown discover type: {discover}')
