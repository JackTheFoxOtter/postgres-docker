from source.modules.logging import get_logger
from hypercorn.asyncio import serve
from hypercorn.config import Config
from source.env import HOST, PORT
from source.app import logger, app
import asyncio


# Configure hypercorn
# See https://pgjones.gitlab.io/hypercorn/how_to_guides/configuring.html#how-to-configure
config = Config()
config.bind = [f"{HOST}:{PORT}"]
config.access_log_format = '%(h)s - "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
config.accesslog = get_logger('hypercorn.access')
config.errorlog = get_logger('hypercorn.error')


logger.info("Starting to serve app...")
asyncio.run(serve(app, config))