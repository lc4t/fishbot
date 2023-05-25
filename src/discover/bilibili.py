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


class BilibiliAPI(object):
    auto_retry = True
    retry_times = 3
    retry_delay = 60  # seconds
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    @classmethod
    async def request_warp(cls, func, *args, **kwargs):
        for i in range(cls.retry_times):
            try:
                resp = await func(*args, **kwargs)
                if resp.get('code') == -401:
                    logger.warning('bilibili api return -401, waiting for 10min')
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
        url = f'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?offset=&host_mid={uid}&timezone_offset=-480&features=itemOpusStyle'
        resp_json = await cls.request_warp(app.ctx.http.get_json, url, headers=cls.headers)
        if not resp_json:
            logger.error(f'get_latest_dynamic failed, uid={uid}')
            return None
        if resp_json.get('code') != 0:
            logger.error(f'get_latest_dynamic return error, uid={uid}, code={resp_json.get("code")}')
            logger.debug(resp_json)
            return None
        return resp_json.get('data', {}).get('items', [])

    @classmethod
    async def get_live_roomid(cls, uid: int):
        if await app.ctx.redis.get(f'bilibili:roomid:{uid}'):
            return await app.ctx.redis.get(f'bilibili:roomid:{uid}')
        url = f'https://api.bilibili.com/x/space/acc/info?mid={uid}'
        resp_json = await cls.request_warp(app.ctx.http.get_json, url, headers=cls.headers)
        if not resp_json:
            logger.error(f'get_live_roomid failed, uid={uid}')
            return None
        if resp_json.get('code') != 0:
            logger.error(f'get_live_room return error, uid={uid}, code={resp_json.get("code")}')
            logger.debug(resp_json)
            return None
        roomid = resp_json.get('data').get('live_room', {}).get('roomid', 0)
        username = resp_json.get('data', {}).get('name', '')

        await app.ctx.redis.set(f'bilibili:username:{uid}', username)
        assert app.ctx.redis.get(f'bilibili:username:{uid}')
        if roomid:
            await app.ctx.redis.setex(f'bilibili:roomid:{uid}', 60 * 60 * 24, roomid)

        return roomid

    @classmethod
    async def get_live_room_info(cls, room_id: int):
        url = f'https://api.live.bilibili.com/room/v1/Room/get_info?room_id={room_id}'
        resp_json = await cls.request_warp(app.ctx.http.get_json, url, headers=cls.headers)
        if not resp_json:
            logger.error(f'get_live_room_info failed, {room_id=}')
            return None
        if resp_json.get('code') != 0:
            logger.error(f'get_live_room_info return error, {room_id=}, code={resp_json.get("code")}')
            logger.debug(resp_json)
            return None
        return resp_json.get('data', {})


class BilibiliDynamic(object):
    @classmethod
    async def new_task(cls, discover, *args, **kwargs):
        # logger.debug(discover)
        if discover.get('type') == 'bilibili.dynamic':
            uid = discover.get('uid')
            handlers = discover.get('handlers')
            senders = discover.get('senders')
            logger.info(f'new task for bilibili.dynamic.dynamic_monitor: \n{json.dumps(discover, indent=4, ensure_ascii=False)}')
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
                name=f'discover=bilibili.dynamic/uid={uid}/handler={handlers}/sender={senders}',
            )
        else:
            logger.warning(f'unknown discover type: {discover}')

    @classmethod
    async def dynamic_monitor(cls, uid, handlers, senders, discover):
        # logger.debug(f'run task for bilibili.dynamic.dynamic_monitor: uid={uid}')
        dynamic_list = None
        cache = await app.ctx.redis.get(f'bilibili.dynamic.{uid}.latest')
        if cache:
            logger.debug(f'bilibili.dynamic.{uid}.latest use cache')
            dynamic_list = json.loads(cache)
        else:
            dynamic_list = await BilibiliAPI.get_user_dynamic(uid)
            if dynamic_list:
                await app.ctx.redis.setex(f'bilibili.dynamic.{uid}.latest', discover.get('iteration', 60) - 3, json.dumps(dynamic_list))
        if not dynamic_list:
            logger.warning(f'get_user_dynamic failed, uid={uid}')
            return
        for dynamic in dynamic_list:
            # redis store
            # call handlers
            # then it call sender
            dynamic_id = dynamic.get('id_str')
            pub_time = dynamic.get('modules', {}).get('module_author', {}).get('pub_ts', 0)
            if time.time() - pub_time > discover.get('max_delay', 600):
                # logger.debug(f'dynamic too old, skip, dynamic_id={dynamic_id}')
                continue
            await app.ctx.redis.set(f'bilibili.dynamic.{uid}.{dynamic_id}', json.dumps(dynamic))
            logger.info(
                f'new task for bilibili.dynamic.dynamic_monitor.new_handler: \ndynamic:\n{json.dumps(dynamic, indent=4, ensure_ascii=False)}\n{handlers=}\n{senders=}'
            )
            app.ctx.scheduler.add_job(
                func=new_handler,
                trigger='date',
                kwargs={
                    'store': 'redis',
                    'store_path': f'bilibili.dynamic.{uid}.{dynamic_id}',
                    'handlers': handlers,
                    'senders': senders,
                },
                next_run_time=datetime.datetime.now(),
                misfire_grace_time=None,
                name=f'handler=bilibili.dynamic/uid={uid}/handler={handlers}/sender={senders}/dynamic_id={dynamic_id}',
            )


class BilibiliLive(object):
    @classmethod
    async def new_task(cls, discover, *args, **kwargs):
        # logger.debug(discover)
        if discover.get('type') == 'bilibili.live':
            uid = discover.get('uid')
            handlers = discover.get('handlers')
            senders = discover.get('senders')
            logger.info(f'new task for bilibili.live.live_monitor: \n{json.dumps(discover, indent=4, ensure_ascii=False)}')
            app.ctx.scheduler.add_job(
                func=cls.live_monitor,
                trigger='interval',
                seconds=discover.get('iteration'),
                kwargs={
                    'uid': uid,
                    'handlers': handlers,
                    'senders': senders,
                    'discover': discover,
                },
                max_instances=1,
                name=f'discover=bilibili.live/uid={uid}/handler={handlers}/sender={senders}',
            )
        else:
            logger.warning(f'unknown discover type: {discover}')

    @classmethod
    async def live_monitor(cls, uid, handlers, senders, discover):
        roomid = discover.get('roomid')
        if not roomid:
            roomid = await BilibiliAPI.get_live_roomid(uid)
        if not roomid:
            logger.warning(f'get roomid failed, uid={uid}')
            return
        # logger.debug(f'run task for bilibili.live.live_monitor: {roomid=}')
        room_info = None
        cache = await app.ctx.redis.get(f'bilibili.live.{roomid}.latest')
        if cache:
            # logger.debug(f'bilibili.live.{roomid}.latest use cache')
            room_info = json.loads(cache)
        else:
            room_info = await BilibiliAPI.get_live_room_info(roomid)
            if room_info:
                await app.ctx.redis.setex(f'bilibili.live.{roomid}.latest', discover.get('iteration', 60) - 3, json.dumps(room_info))

        #
        last_live_start = await app.ctx.redis.get(f'bilibili.live.{roomid}.last_live_start')
        if not last_live_start:
            last_live_start = '0000-00-00 00:00:00'

        now_live_start = room_info.get('live_time', '0000-00-00 00:00:00')

        is_live = room_info.get('live_status', 0) == 1  # 1: live, 2: not live
        #
        k = await calc_hash(roomid, handlers, senders)
        time_windows = await app.ctx.redis.exists(f'bilibili.live.{roomid}.time_windows.{k}')

        # in time_windows only add once
        if is_live and now_live_start > last_live_start and not time_windows:
            logger.info(
                f'new task for bilibili.live.live_monitor.new_handler: \nroom_info:\n{json.dumps(room_info, indent=4, ensure_ascii=False)}\n{handlers=}\n{senders=}'
            )
            app.ctx.scheduler.add_job(
                func=new_handler,
                trigger='date',
                kwargs={
                    'store': 'redis',
                    'store_path': f'bilibili.live.{roomid}.latest',
                    'handlers': handlers,
                    'senders': senders,
                },
                next_run_time=datetime.datetime.now(),
                misfire_grace_time=None,
                name=f'handler=bilibili.live/roomid={roomid}/handler={handlers}/sender={senders}',
            )
            await app.ctx.redis.setex(f'bilibili.live.{roomid}.time_windows.{k}', discover.get('time_window', 120), 1)
            await app.ctx.redis.set(f'bilibili.live.{roomid}.last_live_start', now_live_start)

        # dynamic_id = dynamic.get('id_str')
        # pub_time = dynamic.get('modules', {}).get('module_author', {}).get('pub_ts', 0)

        # await app.ctx.redis.set(f'bilibili.dynamic.{uid}.{dynamic_id}', json.dumps(dynamic))
        # logger.info(
        #     f'new task for bilibili.dynamic.dynamic_monitor.new_handler: \ndynamic:\n{json.dumps(dynamic, indent=4, ensure_ascii=False)}\n{handlers=}\n{senders=}'
        # )
        # app.ctx.scheduler.add_job(
        #     func=new_handler,
        #     trigger='date',
        #     kwargs={
        #         'store': 'redis',
        #         'store_path': f'bilibili.dynamic.{uid}.{dynamic_id}',
        #         'handlers': handlers,
        #         'senders': senders,
        #     },
        #     next_run_time=datetime.datetime.now(),
        #     misfire_grace_time=None,
        #     name=f'handler=bilibili.dynamic/uid={uid}/handler={handlers}/sender={senders}/dynamic_id={dynamic_id}',
        # )


class Bilibili(DiscoverBase):
    @classmethod
    async def new_task(cls, discover, *args, **kwargs):
        if discover.get('type') == 'bilibili.dynamic':
            return await BilibiliDynamic.new_task(discover, *args, **kwargs)
        elif discover.get('type') == 'bilibili.live':
            return await BilibiliLive.new_task(discover, *args, **kwargs)
        else:
            logger.warning(f'unknown discover type: {discover}')
