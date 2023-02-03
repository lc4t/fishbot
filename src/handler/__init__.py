from init import logger, app
from .bilibili import BilibiliHandler
from .normal import NormalHandler
from sender import new_sender
import datetime


async def get_content_from_store(store: str, store_path: str):
    v = None
    if store == 'redis':
        v = await app.ctx.redis.get(store_path)
    else:
        logger.error(f'unknown store type: {store}')
    return v


async def new_handler(store, store_path, handlers, senders, *args, **kwargs):
    # handle the data by handlers.
    content = await get_content_from_store(store, store_path)
    # logger.debug(content)
    for handler in handlers:
        if handler.startswith('bilibili.'):
            content = await BilibiliHandler.new_handler(handler, store, store_path, content, handlers, *args, **kwargs)
        elif handler.startswith('normal.'):
            content = await NormalHandler.new_handler(handler, store, store_path, content, handlers, *args, **kwargs)
        else:
            logger.warning(f'unknown handler type: {handler}')
    logger.info(f'new task for sender:\n{content=}\n{senders=}')
    app.ctx.scheduler.add_job(
        func=new_sender,
        trigger='date',
        kwargs={
            'content': content,
            'senders': senders,
        },
        next_run_time=datetime.datetime.now(),
        misfire_grace_time=None,
        # name=f'sender=bilibili.dynamic/uid={uid}/handler={handler}/sender={sender}/dynamic_id={dynamic_id}',
    )
