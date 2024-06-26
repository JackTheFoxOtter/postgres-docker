#=====================================================================#
#------------------------ [Initialize logging] -----------------------#
#=====================================================================#
from jtfo.logging import setup_logging
import logging

# Configure logging. Sets up custom log level 'notice', custom formatters & root logger
setup_logging(use_colour_if_supported=False) # No need to log to file, supervisor takes care of that
logging.getLogger("asyncio").setLevel(logging.WARNING)
# logging.logAsyncioTasks = False # TODO: Available in Python 3.12, so once the alpine package registry upgrades, we can uncomment this!


#=====================================================================#
#------------------------------- [Setup] -----------------------------#
#=====================================================================#
from source.modules.api_helper import api_method
from source.env import DEBUG, QUART_SECRET_KEY
from quart import Quart
import asyncio
import logging


logger = logging.getLogger('postgres_api')
logger.level = logging.DEBUG if DEBUG else logging.INFO
logger.info(f"Starting Postgres API...")

# Create and configure quart app
quart_app = Quart(
    import_name='postgres_api',
    static_folder='resources/static',
    static_url_path='/static',
    template_folder='resources/templates'
)
quart_app.config['DEBUG'] = DEBUG
quart_app.config['TESTING'] = False
quart_app.config['SECRET_KEY'] = QUART_SECRET_KEY
quart_app.config['EXPLAIN_TEMPLATE_LOADING'] = DEBUG

# Configure event loop
loop = asyncio.get_event_loop()
loop.slow_callback_duration = 0.02 if DEBUG else 0.1 # Everything taking longer than 20 ms should be considered slow
loop.set_debug(DEBUG) # Set asyncio event loop debug mode when launched in debug profile


#=====================================================================#
#--------------------------- [Core Routes] ---------------------------#
#=====================================================================#
from source.modules.backup import get_backups, try_create_backup, try_restore_backup
from werkzeug.exceptions import InternalServerError, BadRequest
from source.modules.utils import filename_validator


@quart_app.post("/echo")
@api_method(sanitize_arguments=False)
async def echo_post(request_data : dict):
    return 200, { "input": request_data }


@quart_app.get('/backups')
@api_method()
async def backups_get(request_data : dict):
    return 200, { 'backups': get_backups() }


@quart_app.post('/backups')
@api_method({
    'database': {
        'allowed_types': [ str ],
        'transformer': lambda x: x.lower()
    },
    'action': {
        'allowed_types': [ str ],
        'allowed_values': ['create', 'restore'],
        'transformer': lambda x: x.lower()
    },
    'filename': {
        'allowed_types': [ str ],
        'validator': filename_validator
    }
})
async def backups_post(request_data : dict):
    """
    Create a new backup or restore an existing one.

    """
    database = request_data['database']
    action = request_data['action']
    filename = request_data['filename']
    
    if database == 'postgres':
        raise BadRequest("Database name cannot be 'postgres'!")

    if action == 'create':
        # Create new backup
        success, filename = await try_create_backup(database, filename)
        if not success:
            raise InternalServerError("Backup was not created!")

    elif action == 'restore':
        # Restore from existing backup
        success = await try_restore_backup(database, filename)
        if not success:
            raise InternalServerError("Backup was not restored! This might be super bad!")

    return 200, { 'database': database, 'action': action, 'name': filename }
