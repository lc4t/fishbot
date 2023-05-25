from init import app, logger
from sender.base import SenderBase
import datetime
import asyncio


class SenderCQ(SenderBase):
    @classmethod
    async def send_msg(cls, url: str, api: str, access_token: str, target_type: str, target: str, message: str):
        # DOC: https://docs.go-cqhttp.org/api/#%E5%8F%91%E9%80%81%E6%B6%88%E6%81%AF
        logger.debug(f'send_msg: {url}{api} {target_type}, {target}, {message}')
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        resp = await app.ctx.http.post_json(
            url=f'{url}{api}',
            headers=headers,
            json={
                # 'type': target_type,
                f'{target_type}_id': int(target),
                'message': message,
                'auto_escape': False,
            },
        )
        return resp

    @classmethod
    async def new_sender(cls, content, sender, send_hash, retry_times=3, retry_delay=60, *args, **kwargs):
        # logger.debug(sender)
        async with app.ctx.sender_cq_lock:
            # logger.info('---------')
            # logger.info(send_hash)
            # logger.info(await app.ctx.redis.get(send_hash) in ['success'])
            # x = await app.ctx.redis.get(send_hash)
            # logger.info(type(x))
            # logger.info(x)
            if await app.ctx.redis.get(send_hash) in ['success']:
                logger.warning(f'send_hash={send_hash} already sent')
                return
            if sender.get('type') == 'cq.send_msg':
                url = sender.get('url')
                api = sender.get('api')
                access_token = sender.get('access_token')
                target_type = sender.get('target_type')
                target = sender.get('target')
                if content is None or len(content) == 0:
                    # logger.info(f'[{content}]')
                    # logger.warning(f'content is empty')
                    await app.ctx.redis.set(send_hash, 'success')
                    return
                resp = await cls.send_msg(url, api, access_token, target_type, target, content)
                logger.info(resp)
                if resp.get('retcode') == 0:
                    logger.info(f'success send: \n{content}')
                    await app.ctx.redis.set(send_hash, 'success')
                else:
                    logger.warning(f'send_msg failed, {resp}')
                    await app.ctx.redis.set(send_hash, 'failed')
                recheck = await app.ctx.redis.get(send_hash)
                logger.debug(f'redis check: {send_hash} -> {recheck}')
            else:
                logger.warning(f'unknown sender type: {sender}')
            # logger.info('+++++++++++')
