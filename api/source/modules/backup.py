from source.modules.utils import execute_subprocess_shell, get_timestamped_filename, get_unique_filename
from source.env import DB_CONN_SYNC, BACKUP_PATH
from source.modules.logging import get_logger
from urllib.parse import urlparse
from typing import Dict, Tuple
import os


PARSED_DB_CONN = urlparse(DB_CONN_SYNC)
logger = get_logger('postgres_api.database_backup')


async def try_create_backup(backup_name : str) -> Tuple[bool, str]:
    logger.info(f"Attempting to create database backup '{backup_name}'...)")
    try:
        scheme = str(PARSED_DB_CONN.scheme).lower()
        if scheme != 'postgresql': 
            raise Exception(f"Unsupported scheme in connection URL: '{scheme}'")
        
        backup_file_name = get_unique_filename(BACKUP_PATH, get_timestamped_filename(backup_name, scheme))
        backup_file_path = os.path.join(BACKUP_PATH, backup_file_name)
        returncode = await execute_subprocess_shell(logger, 'pg_dump', f'pg_dump --dbname="{DB_CONN_SYNC}" > "{backup_file_path}"')
        if returncode > 0:
            raise Exception("Subprocess returncode does not indicate success!")

        logger.info(f"Successfully completed database backup '{backup_name}'! (-> '{backup_file_path}')")
        return True, backup_file_name
    
    except Exception:
        logger.exception(f"BACKUP FAILED! Exception happened during database backup '{backup_name}'!")
        return False, ""


async def try_restore_backup(backup_file_name : str) -> bool:
    logger.info(f"Attempting to restore database from backup file '{backup_file_name}'...")
    try:
        scheme = str(PARSED_DB_CONN.scheme).lower()
        if scheme != 'postgresql': 
            raise Exception(f"Unsupported scheme in connection URL: '{scheme}'")

        backup_file_path = os.path.join(BACKUP_PATH, backup_file_name)
        if not os.path.exists(backup_file_path): raise Exception(f"Backup file '{backup_file_name}' doesn't exist!")
        raise NotImplementedError() # TODO Postgres DB restore procedure
        return True
    
    except Exception:
        logger.exception(f"RESTORE FAILED! Exception happened during database restore from backup file '{backup_file_name}'!")
        return False


def get_backup_files() -> Dict[str, str]:
    logger.debug(f"Fetching backup file list...")
    return { os.path.split(path)[-1]: path for path in os.listdir() if os.path.isfile(path) }