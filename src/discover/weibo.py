from init import logger
import asyncio
from init import app
import json
import time
import datetime
from discover.base import DiscoverBase
from handler import new_handler
from core.utils import calc_hash

# async def get(a, *args, **kwargs):
#     logger.info(a)
#     logger.info(args)
#     logger.info(kwargs)


class WeiboAPI(object):
    auto_retry = True
    retry_times = 3
    retry_delay = 60  # seconds
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'cookie': app.ctx.toml.get('conf', {}).get('weibo_cookie', ''),
        'accept-language': 'zh-CN,zh;q=0.9',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    @classmethod
    async def request_warp(cls, func, *args, **kwargs):
        for i in range(cls.retry_times):
            try:
                resp = await func(*args, **kwargs)
                if resp.get('code') == -401:
                    logger.warning('weibo api waf')
                    await asyncio.sleep(60 * 10)
                    is_waf = True
                    continue
                is_waf = False
                return resp
            except Exception as e:
                logger.error(e)
                logger.error(f'retry {i+1}/{cls.retry_times} times')
                await asyncio.sleep(cls.retry_delay * (i + 1))
        return None

    @classmethod
    async def get_user_dynamic(cls, uid, *args, **kwargs):
        url = f'https://weibo.com/ajax/statuses/mymblog?uid={uid}&page=1&feature=0'
        resp_json = await cls.request_warp(app.ctx.http.get_json, url, headers=cls.headers)
        if not resp_json:
            logger.error(f'get_latest_dynamic failed, uid={uid}')
            return None
        if resp_json.get('ok') != 1:
            logger.error(f'get_latest_dynamic return error, uid={uid}')
            logger.debug(resp_json)
            return None
        return resp_json.get('data', {}).get('list', [])


class WeiboDynamic(object):
    @classmethod
    async def new_task(cls, discover, *args, **kwargs):
        if discover.get('type') == 'weibo.dynamic':
            uid = discover.get('uid')
            handlers = discover.get('handlers')
            senders = discover.get('senders')
            logger.info(f'new task for weibo.dynamic.dynamic_monitor: \n{json.dumps(discover, indent=4, ensure_ascii=False)}')
            app.ctx.scheduler.add_job(
                func=cls.dynamic_monitor,
                trigger='interval',
                seconds=discover.get('iteration'),
                kwargs={
                    'uid': uid,
                    'handlers': handlers,
                    'senders': senders,
                    'discover': discover,
                },
                max_instances=1,
                name=f'discover=weibo.dynamic/uid={uid}/handler={handlers}/sender={senders}',
            )
        else:
            logger.warning(f'unknown discover type: {discover}')

    @classmethod
    async def dynamic_monitor(cls, uid, handlers, senders, discover):
        dynamic_list = None
        cache = await app.ctx.redis.get(f'weibo.dynamic.{uid}.latest')
        if cache:
            logger.debug(f'weibo.dynamic.{uid}.latest use cache')
            dynamic_list = json.loads(cache)
        else:
            dynamic_list = await WeiboAPI.get_user_dynamic(uid)
            if dynamic_list:
                await app.ctx.redis.setex(f'weibo.dynamic.{uid}.latest', discover.get('iteration', 60) - 3, json.dumps(dynamic_list))
        if not dynamic_list:
            logger.warning(f'get_user_dynamic failed, uid={uid}')
            return
        for dynamic in dynamic_list:
            dynamic_id = dynamic.get('idstr')
            pub_time = dynamic.get('created_at')
            pub_time = time.mktime(time.strptime(pub_time, '%a %b %d %H:%M:%S +0800 %Y'))
            if time.time() - pub_time > discover.get('max_delay', 600):
                continue
            await app.ctx.redis.set(f'weibo.dynamic.{uid}.{dynamic_id}', json.dumps(dynamic))
            logger.info(
                f'new task for weibo.dynamic.dynamic_monitor.new_handler: \ndynamic:\n{json.dumps(dynamic, indent=4, ensure_ascii=False)}\n{handlers=}\n{senders=}'
            )
            app.ctx.scheduler.add_job(
                func=new_handler,
                trigger='date',
                kwargs={
                    'store': 'redis',
                    'store_path': f'weibo.dynamic.{uid}.{dynamic_id}',
                    'handlers': handlers,
                    'senders': senders,
                },
                next_run_time=datetime.datetime.now(),
                misfire_grace_time=None,
                name=f'handler=weibo.dynamic/uid={uid}/handler={handlers}/sender={senders}/dynamic_id={dynamic_id}',
            )


class Weibo(DiscoverBase):
    @classmethod
    async def new_task(cls, discover, *args, **kwargs):
        if discover.get('type') == 'weibo.dynamic':
            return await WeiboDynamic.new_task(discover, *args, **kwargs)
        else:
            logger.warning(f'unknown discover type: {discover}')
