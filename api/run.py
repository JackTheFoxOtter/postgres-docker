#=====================================================================#
#------------------------- [Start Application] -----------------------#
#=====================================================================#
from source.env import ENVIRONMENT, DEBUG, QUART_HOST, QUART_PORT
from source.app import logger, app
import asyncio
import sys

logger.info(f"Environment: {ENVIRONMENT}; Debug: {str(DEBUG)}; Python: {sys.version}")

environment = ENVIRONMENT.lower()
if environment in [ 'production', 'prod' ]:
    # Production environment
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    import logging

    # Configure hypercorn
    # See https://pgjones.gitlab.io/hypercorn/how_to_guides/configuring.html#how-to-configure
    config = Config()
    config.bind = [f"{QUART_HOST}:{QUART_PORT}"]
    config.access_log_format = '%(h)s - "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
    config.accesslog = logging.getLogger('hypercorn.access')
    config.errorlog = logging.getLogger('hypercorn.error')

    logger.info("Starting to serve app...")
    asyncio.run(serve(app, config))

elif environment in [ 'development', 'dev', 'test', 'testing' ]:
    from source.patcher import apply_patches

    # Testing environment
    logger.info("Starting to serve app (integrated debug server)...")
    apply_patches() # Custom logger injection for debug environment
    app.run(
        host=QUART_HOST,
        port=QUART_PORT,
        loop=asyncio.get_event_loop(),
        debug=DEBUG
    )

else:
    # Unkown environment
    raise Exception(f"Unknown Environment: {ENVIRONMENT}")