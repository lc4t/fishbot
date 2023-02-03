import logging
import os
import tomllib
import sentry_sdk
from loguru import logger
from sanic import Sanic
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sanic import SanicIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO, event_level=logging.ERROR  # Capture info and above as breadcrumbs  # Send errors as events
)

# sentry_sdk.init(
#     dsn="https://2157eedaf6d349e0b4cb5f69d8e8c63b@o79992.ingest.sentry.io/4504491658248192",
#     integrations=[
#         SanicIntegration(),
#     ],
#     environment=os.getenv('RUN_MODE', 'None'),
#     traces_sample_rate=1.0,
# )
import sys

logger.remove()
logger.add(sys.stderr, level='DEBUG' if os.getenv('RUN_MODE').upper() == 'DEV' else 'INFO')
logger.add('/app/log/debug.log', level='DEBUG', retention='3 days', enqueue=True, rotation="500 MB", compression='zip')
logger.add('/app/log/info.log', level='INFO', retention='3 days', enqueue=True, rotation="12:00", compression='zip')
logger.add('/app/log/error.log', level='ERROR', retention='7 days', enqueue=True)


app = Sanic('fishbot')

app.ctx.toml = tomllib.load(open('./config.toml', 'rb'))
