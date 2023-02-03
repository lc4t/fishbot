from init import app, logger


class HandlerBase(object):
    pass
    # @classmethod
    # async def get_content_from_store(cls, store, store_path):
    #     v = None
    #     if store == 'redis':
    #         v = await app.ctx.redis.get(store_path)
    #     else:
    #         logger.error(f'unknown store type: {store}')
    #     return v

    # if type == 'bilibili.dynamic':
    #     return json.loads(v)
    # else:
    #     logger.warning(f'unknown handler type: {type}')
    #     return v
