# 初始化DB
import os

from tortoise.contrib.sanic import register_tortoise


async def get_sql(app):
    from loguru import logger
    from tortoise import Tortoise
    from tortoise.utils import get_schema_sql

    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    db = os.getenv('DB_DATABASE')

    await Tortoise.init(
        db_url=f"mysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4",
        modules={
            'models': ["core.models"],
        },
    )
    conn = Tortoise.get_connection('default')
    sql = get_schema_sql(conn, True)
    logger.info(sql)


def init_db(app):
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    db = os.getenv('DB_DATABASE')
    register_tortoise(
        app,
        config={
            'connections': {
                'default': f"mysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4",
            },
            'apps': {
                'models': {
                    'models': ["core.models"],
                    'default_connection': 'default',
                },
            },
            'timezone': os.getenv('TZ', 'Asia/Shanghai'),
        },
        generate_schemas=False,
    )
