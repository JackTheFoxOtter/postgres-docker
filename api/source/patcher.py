from hypercorn.config import Config as HyperConfig
from typing import Awaitable, Callable, Coroutine
from hypercorn.asyncio import serve
from quart import Quart
import logging


logger = logging.getLogger('patcher')


def run_task(
    self,
    host: str = "127.0.0.1",
    port: int = 5000,
    debug: bool | None = None,
    ca_certs: str | None = None,
    certfile: str | None = None,
    keyfile: str | None = None,
    shutdown_trigger: Callable[..., Awaitable[None]] | None = None,
) -> Coroutine[None, None, None]:
    """Patch for run_task in Quart-class to inject custom loggers.
    
    Return a task that when awaited runs this application.

    This is best used for development only, see Hypercorn for
    production servers.

    Arguments:
        host: Hostname to listen on. By default this is loopback
            only, use 0.0.0.0 to have the server listen externally.
        port: Port number to listen on.
        debug: If set enable (or disable) debug mode and debug output.
        ca_certs: Path to the SSL CA certificate file.
        certfile: Path to the SSL certificate file.
        keyfile: Path to the SSL key file.

    """
    # See https://pgjones.gitlab.io/hypercorn/how_to_guides/configuring.html#how-to-configure
    config = HyperConfig()
    config.access_log_format = '%(h)s - "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
    config.accesslog = logging.getLogger('hypercorn.access')
    config.errorlog = logging.getLogger('hypercorn.error')
    config.bind = [f"{host}:{port}"]
    config.ca_certs = ca_certs
    config.certfile = certfile
    if debug is not None:
        self.debug = debug
    config.keyfile = keyfile

    return serve(self, config, shutdown_trigger=shutdown_trigger)


def apply_patches():
    logger.info("Patching Quart.run_task to enable custom logging for hypercorn in debug mode...")
    Quart.run_task = run_task