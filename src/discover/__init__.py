from init import logger
from .bilibili import Bilibili
from .weibo import Weibo


async def new_task(discover, *args, **kwargs):
    if discover.get('type').startswith('bilibili.'):
        return await Bilibili.new_task(discover, *args, **kwargs)
    elif discover.get('type').startswith('weibo.'):
        return await Weibo.new_task(discover, *args, **kwargs)
    else:
        logger.warning(f'unknown discover type: {discover}')
