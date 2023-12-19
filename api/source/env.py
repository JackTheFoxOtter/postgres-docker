import argparse
import os

parser = argparse.ArgumentParser()
# Global arguments
parser.add_argument('-e', '--environment', type=str, help="Environment of the app, defaults to 'production'")
parser.add_argument('-d', '--debug', action='store_true', help="Enable debug output, defaults to False")
parser.add_argument('-pb', '--path_backups', type=str, help="Path for backup files, defaults to '/backups'")
parser.add_argument('-pl', '--path_logs', type=str, help="Path for log files, defaults to '/logs'")
# Database arguments
parser.add_argument('-ds', '--database_conn_sync', type=str, help="Sync database connection string, without database name")
parser.add_argument('-da', '--database_conn_async', type=str, help="Async database connection string, without database name")
# Quart arguments
parser.add_argument('-qh', '--quart_host', type=str, help="Host-IP of the Quart webserver, defaults to '127.0.0.1'")
parser.add_argument('-qp', '--quart_port', type=int, help="Host-Port of the Quart webserver, defaults to 5000")
parser.add_argument('-qs', '--quart_secret_key', type=str, help="Secret key for Quart webserver")
args = parser.parse_args()

# Global constants
ENVIRONMENT = (args.environment or os.getenv('ENVIRONMENT') or 'production').lower()
DEBUG = args.debug or bool(os.getenv('DEBUG')) or False
PATH_BACKUPS = args.path_backups or os.getenv('PATH_BACKUPS') or '/backups'
PATH_LOGS = args.path_logs or os.getenv('PATH_LOGS') or '/logs'
# Databbase constants
DB_CONN_SYNC = args.database_conn_sync or os.getenv('DB_CONN_SYNC')
DB_CONN_ASYNC = args.database_conn_async or os.getenv('DB_CONN_ASYNC')
# Quart constants
QUART_HOST = args.quart_host or os.getenv('QUART_HOST') or '127.0.0.1'
QUART_PORT = args.quart_port or int(os.getenv('QUART_PORT')) if os.getenv('QUART_PORT') else None or 5000
QUART_SECRET_KEY = args.quart_secret_key or os.getenv('QUART_SECRET_KEY')

# Environment validation
if not DB_CONN_SYNC: raise Exception("No sync database connection string specified!")
if not DB_CONN_ASYNC: raise Exception("No async database connection string specified!")
if not QUART_SECRET_KEY: raise Exception("No secret key specified!")
