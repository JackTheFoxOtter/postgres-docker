from asyncio import get_event_loop
from source.app import logger, app
from source.env import HOST, PORT, IS_DEBUG


logger.info("Starting to serve app (integrated debug server)...")
app.run(
    host=HOST,
    port=PORT,
    loop=get_event_loop(),
    debug=IS_DEBUG
)