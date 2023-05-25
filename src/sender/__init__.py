from init import app, logger
from hashlib import sha512
import asyncio
import datetime
from .cq import SenderCQ
from core.utils import calc_hash


async def new_sender(content, senders, retry_times=10, *args, **kwargs):
    # calc hash
    failed = 0
    retrys = []
    for sender in senders:
        if sender.get('name') and app.ctx.toml.get('sender').get(sender.get('name')):
            # update user default value
            # logger.debug('update sender default value')
            sender.update(app.ctx.toml.get('sender').get(sender.get('name')))
        async with app.ctx.sender_init_lock:
            send_hash = await calc_hash(content, sender)
            # check if send_hash exists

            if await app.ctx.redis.exists(send_hash) and await app.ctx.redis.get(send_hash) == 'success':
                logger.debug(f'send_hash({send_hash}) success')
                continue

            if (not await app.ctx.redis.exists(send_hash)) or (
                await app.ctx.redis.exists(send_hash) and await app.ctx.redis.get(send_hash) not in ['success', 'pass']
            ):

                # need to send, add job
                logger.debug(f'send_hash({send_hash}) job added')
                if sender.get('type').startswith('cq.'):
                    # send by cqhttp
                    logger.info(f'new task for senderCQ.new_sender:\n{content=}\n{sender=}\n{send_hash=}')
                    app.ctx.scheduler.add_job(
                        func=SenderCQ.new_sender,
                        trigger='date',
                        kwargs={
                            'content': content,
                            'sender': sender,
                            'send_hash': send_hash,
                        },
                        next_run_time=datetime.datetime.now(),
                        misfire_grace_time=None,
                        max_instances=1,
                        name=f'sender={send_hash}/send=cq',
                    )
                else:
                    logger.error(f'unknown sender type: {sender.get("type")}')
            if await app.ctx.redis.exists(send_hash) and await app.ctx.redis.exists(send_hash) in ['failed']:
                failed += 1
                retrys.append(sender)

    # check retry times
    if retry_times > 0 and failed:
        logger.info(f'retry task for :\n{content=}\n{retrys=}')
        app.ctx.scheduler.add_job(
            func=new_sender,
            trigger='date',
            kwargs={
                'content': content,
                'senders': retrys,
                'retry_times': retry_times - 1,
            },
            next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=app.ctx.toml.get('conf').get('sender_retry_delay', 10)),
            misfire_grace_time=None,
            max_instances=1,
            name=f'sender={send_hash}/retry',
        )
