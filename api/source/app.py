#=====================================================================#
#------------------------ [Initialize logging] -----------------------#
#=====================================================================#
from source.modules.logging import setup_logging, get_logger
from source.modules.utils import get_timestamped_filename
import os

log_file_path = os.path.join('/logs', get_timestamped_filename('postgres_api', 'log'))
setup_logging(log_file_path)

logger = get_logger('postgres_api.core')


#=====================================================================#
#----------------------------- [Imports] -----------------------------#
#=====================================================================#
from source.modules.backup import get_backup_files, try_create_backup, try_restore_backup
from source.modules.api_helper import api_method
from source.modules.utils import filename_validator
from source.env import HOST, PORT, IS_DEBUG, SECRET_KEY
from werkzeug.exceptions import InternalServerError, Conflict
from quart import Quart, Response, request
from typing import Any, List
import asyncio


#=====================================================================#
#------------------------------- [Setup] -----------------------------#
#=====================================================================#
logger.info(f"Starting Postgres API...")

# Create and configure quart app
app = Quart(
    import_name='postgres_api',
    static_folder='resources/static',
    static_url_path='/static',
    template_folder='resources/templates'
)
app.config['DEBUG'] = IS_DEBUG
app.config['TESTING'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['EXPLAIN_TEMPLATE_LOADING'] = IS_DEBUG

# Configure event loop
loop = asyncio.get_event_loop()
loop.slow_callback_duration = 0.02 if IS_DEBUG else 0.1 # Everything taking longer than 10 ms should be considered slow
loop.set_debug(IS_DEBUG) # Set asyncio event loop debug mode when launched in debug profile


#=====================================================================#
#--------------------------- [Core Routes] ---------------------------#
#=====================================================================#
@app.post("/echo")
@api_method(sanitize_arguments=False)
async def echo_post(request_data):
    return 200, { "input": request_data }

@app.get('/backups')
@api_method()
async def backups_get(request_data):
    return 200, { 'backups': [ name for name in get_backup_files().keys() ] }

@app.post('/backups')
@api_method({
    'action': {
        'allowed_types': [ str ],
        'allowed_values': ['create', 'restore'],
        'transformer': lambda x: x.lower()
    },
    'name': {
        'allowed_types': [ str ],
        'validator': filename_validator
    }
})
async def backups_post(request_data):
    """
    Create a new backup or restore an existing one.
    When restoring, a pre-restore backup is automatically created.

    """
    filename = request_data['name']
    action = request_data['action']
    
    existing_backup_files = get_backup_files()
    
    if action == 'create':
        # Create new backup
        success, filename = await try_create_backup(filename)
        if not success:
            raise InternalServerError("Backup was not created!")

    elif action == 'restore':
        # Restore from existing backup
        filepath = existing_backup_files[filename]
        raise InternalServerError("Action not implemented!")

    return 200, { 'action': action, 'name': filename }

