import os
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from init import logger
from init import app

# from discover.bilibili import Bilibili
from discover import new_task
import re


async def scheduler():
    logger.info('scheduler entrypoint')
    DB = app.ctx.scheduler_db
    REDIS = {
        'host': os.getenv('REDIS_HOST'),
        'port': os.getenv('REDIS_PORT'),
        'db': DB,
        'password': os.getenv('REDIS_PASSWORD', ''),
    }
    scheduler_job_defaults = {
        # 'jobstore': 'default',
        'coalesce': True,  # True: last missing False: all missing
        'misfire_grace_time': 60 * 10,  # forward seconds
        'max_instances': 1,
        'replace_existing': True,
    }
    config = {
        'job_defaults': scheduler_job_defaults,
        'timezone': os.getenv('TZ', 'Asia/Shanghai'),
        'jobstores': {'default': RedisJobStore(jobs_key='dispatched_trips_jobs', run_times_key='dispatched_trips_running', **REDIS)},
    }
    app.ctx.scheduler = AsyncIOScheduler(**config)
    app.ctx.scheduler.start()
    logger.info('scheduler started')


async def task_detect_from_toml(toml):
    logger.info('task_detect_from_toml entrypoint')
    discovers = toml.get('discover')
    # logger.info(discovers)

    for discover in discovers:
        await new_task(discover)
