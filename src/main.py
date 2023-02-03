import asyncio
import os

import aiohttp
import tomllib
from init import logger
from sanic import response

from core.db import init_db
from core.http import HTTP
from core.redis import Redis
from core.scheduler import scheduler, task_detect_from_toml
from init import app

init_db(app)


@app.listener('before_server_start')
def init(app, loop):
    # init aiohttp session, redis
    app.ctx.loop = loop
    app.ctx.aiohttp_sem = asyncio.Semaphore(os.getenv('AIOHTTP_MAX_CONNECTIONS', 1))
    app.ctx.aiohttp_session = aiohttp.ClientSession(loop=loop)
    app.ctx.http = HTTP(app)
    app.ctx.redis_instance = Redis(app)
    app.ctx.sender_init_lock = asyncio.Lock()
    app.ctx.sender_cq_lock = asyncio.Lock()
    app.ctx.scheduler_db = 1


@app.listener('before_server_start')
def init(app):
    # init global variable
    app.ctx.CORE_QUEUE = 'core:task_queue'
    logger.info('load toml')


@app.listener('before_server_start')
async def init(app, loop):
    app.ctx.redis = await app.ctx.redis_instance.get()
    for dbid in [app.ctx.scheduler_db]:
        x = await app.ctx.redis.flushdb(dbid)
        logger.info(f'redis {dbid} flush {x}')


@app.listener('after_server_stop')
def finish(app, loop):
    loop.run_until_complete(
        asyncio.wait(
            [
                app.ctx.aiohttp_session.close(),
                app.ctx.scheduler.shutdown(),
                app.ctx.redis_instance.close(),
            ]
        )
    )
    loop.close()


@app.route('/')
async def test(request):
    return response.text('Hello World!')


# @app.route('/jobs')
# async def test(request):
#     auth = request.headers.get("auth")
#     if auth != os.getenv('HEADERS_AUTH', 'fishbot'):
#         return response.text('UNAUTHORIZED')
#     jobs = request.app.ctx.scheduler.get_jobs()
#     job_items = []
#     for job in jobs:
#         job_items.append(
#             {
#                 'id': job.id,
#                 'name': job.name,
#                 'next_run_time': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S'),
#                 'trigger': job.trigger.__str__(),
#                 # 'trigger_interval': job.trigger.interval.seconds if job.trigger.interval else '0',
#                 'start_date': job.trigger.start_date.strftime('%Y-%m-%d %H:%M:%S') if job.trigger.start_date else None,
#                 'end_date': job.trigger.end_date.strftime('%Y-%m-%d %H:%M:%S') if job.trigger.end_date else None,
#                 'args': job.args[1:],
#                 'kwargs': str(job.kwargs),
#             }
#         )
#     text = 'ID|NAME|NEXT_RUN_TIME|TRIGGER|START_DATE|END_DATE|ARGS|KWARGS\n'
#     for one in job_items:
#         text += '{}|{}|{}|{}|{}|{}|{}|{}\n'.format(
#             one['id'],
#             one['name'],
#             one['next_run_time'],
#             one['trigger'],
#             one['start_date'],
#             one['end_date'],
#             one['args'],
#             one['kwargs'],
#         )
#     return response.text(text)
#     # logger.info(
#     #     f'{job.id} @{job.next_run_time} {job.trigger.start_date}->{job.trigger.end_date}(mis: {job.misfire_grace_time}) {job.args}'
#     # )
#     # logger.info('Here is your log')
#     # return response.text(json.dumps(job_items))


app.add_task(scheduler())
app.add_task(task_detect_from_toml(app.ctx.toml))
# 1. detect toml config, make scheduler tasks
# 2.

# if os.getenv('RUN_MODE') not in ['DEV']:
#     # 启动JOB调度器
#     logger.info('MAIN LOOP')
#     for task in [
#         _job_crontab_user(BiliJobGenerator.from_user_info_to_job),  # 1
#     ]:
#         app.add_task(task)


if __name__ == "__main__":
    wokers = int(os.getenv('WORKERS', 1))
    env = os.getenv('RUN_MODE', 'PROD').upper()
    if env == 'DEV':
        app.run(access_log=True, dev=True, host='0.0.0.0', port=1337, workers=wokers)
    else:
        app.run(access_log=True, dev=False, host='0.0.0.0', port=1337, workers=wokers)
