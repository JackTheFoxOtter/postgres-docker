#=====================================================================#
#------------------------ [Initialize logging] -----------------------#
#=====================================================================#
from .modules.logging import setup_logging, get_logger

setup_logging()

logger = get_logger('postgres_api.core')


#=====================================================================#
#----------------------------- [Imports] -----------------------------#
#=====================================================================#
from .env import HOST, PORT, IS_DEBUG, SECRET_KEY
from quart import Quart
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
@app.route('/')
async def home():
    """
    Internal redirect to home page

    """
    return 'ABC'