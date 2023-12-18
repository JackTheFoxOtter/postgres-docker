from source.modules.utils import execute_subprocess_shell, get_timestamped_filename, get_unique_filename
from source.env import DB_CONN_SYNC, PATH_BACKUPS
from urllib.parse import urlparse
from typing import List, Tuple
import logging
import os


PARSED_DB_CONN = urlparse(DB_CONN_SYNC)
logger = logging.getLogger('database_backup')


def get_backups() -> List[str]:
    logger.debug(f"Fetching backup file list...")
    return [ path for path in os.listdir(PATH_BACKUPS) ]


async def try_create_backup(database : str, backup_name : str) -> Tuple[bool, str]:
    logger.info(f"Attempting to create database backup '{backup_name}'...)")
    try:
        scheme = str(PARSED_DB_CONN.scheme).lower()
        if scheme != 'postgresql':
            raise Exception(f"Unsupported scheme in connection URL: '{scheme}'")
        
        dbname = os.path.join(DB_CONN_SYNC, database)
        backup_file_name = get_unique_filename(PATH_BACKUPS, get_timestamped_filename(f"{database}_{backup_name}", f"{scheme}.gz"))
        backup_file_path = os.path.join(PATH_BACKUPS, backup_file_name)
        if await execute_subprocess_shell(logger, 'create_backup', f'/api/scripts/create_backup.sh "{dbname}" "{backup_file_path}"') > 0:
            raise Exception("Failed to create backup!")

        logger.info(f"Successfully backed up database '{backup_name}'! (-> '{backup_file_path}')")
        return True, backup_file_name
    
    except Exception:
        logger.exception(f"BACKUP FAILED! Exception happened during database backup '{backup_name}'!")
        return False, ""


async def try_restore_backup(database : str, backup_file_name : str) -> bool:
    logger.info(f"Attempting to restore database from backup file '{backup_file_name}'...")
    try:
        scheme = str(PARSED_DB_CONN.scheme).lower()
        if scheme != 'postgresql': 
            raise Exception(f"Unsupported scheme in connection URL: '{scheme}'")

        backup_file_path = os.path.join(PATH_BACKUPS, backup_file_name)
        if await execute_subprocess_shell(logger, 'restore_backup', f'/api/scripts/restore_backup.sh "{database}" "{backup_file_path}"') > 0:
            raise Exception("Failed to restore backup!")
        
        logger.info(f"Successfully restored database from backup '{backup_file_path}'!")
        return True
    
    except Exception:
        logger.exception(f"RESTORE FAILED! Exception happened during database restore from backup file '{backup_file_name}'!")
        return False
