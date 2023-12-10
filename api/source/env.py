import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-ht', '--host', type=str, help="Host-IP of the webserver, defaults to 127.0.0.1")
parser.add_argument('-pt', '--port', type=int, help="Host-Port of the webserver, defaults to 5000")
parser.add_argument('-d', '--debug', action='store_true', help="Enable debug output")
parser.add_argument('-dbs', '--database_connection_sync', type=str, help="Sync Database Connection String")
parser.add_argument('-dba', '--database_connection_async', type=str, help="Async Database Connection String")
parser.add_argument('-s', '--secret_key', type=str, help="Secret key for Quart")
parser.add_argument('-bp', '--backup_path', type=str, help="Path for backup files")
parser.add_argument('-lp', '--log_path', type=str, help="Path for log files")
args = parser.parse_args()

HOST = args.host or os.getenv('HOST') or '127.0.0.1'
PORT = args.port or int(os.getenv('PORT')) if os.getenv('PORT') else None or 5000
IS_DEBUG = args.debug or bool(os.getenv('DEBUG'))
DB_CONN_SYNC = args.database_connection_sync or os.getenv('DB_CONN_SYNC')
DB_CONN_ASYNC = args.database_connection_async or os.getenv('DB_CONN_ASYNC')
SECRET_KEY = args.secret_key or os.getenv('SECRET_KEY')
BACKUP_PATH = args.backup_path or os.getenv('BACKUP_PATH') or '/backups/'
LOG_PATH = args.log_path or os.getenv('LOG_PATH') or '/logs/'

if not DB_CONN_SYNC: raise Exception("No sync database connection string specified!")
if not DB_CONN_ASYNC: raise Exception("No async database connection string specified!")
if not SECRET_KEY: raise Exception("No secret key specified!")
