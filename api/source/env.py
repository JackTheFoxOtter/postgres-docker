import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-ht', '--host', type=str, help="Host-IP of the webserver, defaults to 127.0.0.1")
parser.add_argument('-pt', '--port', type=int, help="Host-Port of the webserver, defaults to 5000")
parser.add_argument('-d', '--debug', action='store_true', help="Enable debug output")
parser.add_argument('-s', '--secret_key', type=str, help="Secret key for Quart")
args = parser.parse_args()

HOST = args.host or os.getenv('HOST') or '127.0.0.1'
PORT = args.port or int(os.getenv('PORT')) if os.getenv('PORT') else None or 5000
IS_DEBUG = args.debug or bool(os.getenv('DEBUG'))
SECRET_KEY = args.secret_key or os.getenv('SECRET_KEY')

if not SECRET_KEY: raise Exception("No secret key specified!")
