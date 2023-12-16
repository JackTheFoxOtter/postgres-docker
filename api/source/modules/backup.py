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
        if await execute_subprocess_shell(logger, 'pg_dump', f'pg_dump --dbname="{dbname}" | gzip > "{backup_file_path}"') > 0:
            raise Exception("Subprocess returncode does not indicate success!")

        logger.info(f"Successfully completed database backup '{backup_name}'! (-> '{backup_file_path}')")
        return True, backup_file_name
    
    except Exception:
        logger.exception(f"BACKUP FAILED! Exception happened during database backup '{backup_name}'!")
        return False, ""


async def try_restore_backup(database : str, backup_name : str) -> bool:
    logger.info(f"Attempting to restore database from backup file '{backup_name}'...")
    try:
        scheme = str(PARSED_DB_CONN.scheme).lower()
        if scheme != 'postgresql': 
            raise Exception(f"Unsupported scheme in connection URL: '{scheme}'")

        backup_file_path = os.path.join(PATH_BACKUPS, backup_name)
        if not os.path.exists(backup_file_path):
            raise Exception(f"Backup file '{backup_file_path}' doesn't exist!")

        logger.info(f"Database restore 1/4: Re-creating 'tempdb'...")
        if await execute_subprocess_shell(logger, 'dropdb', f'dropdb \'tempdb\' --force --if-exists -U postgres') > 0:
            raise Exception("Failed to drop temporary resoration database!")
        if await execute_subprocess_shell(logger, 'createdb', f'createdb \'tempdb\' -U postgres') > 0:
            raise Exception("Failed to create temporary restoration database!")

        logger.info(f"Database restore 2/4: Populating 'tempdb' from backup '{backup_name}'...")
        if await execute_subprocess_shell(logger, 'psql', f'gunzip < \'{os.path.join(PATH_BACKUPS, backup_name)}\' | psql \'tempdb\' -U postgres') > 0:
            raise Exception("Failed to populate temporary restoration database from backup file! (Is the file corrupt?)")

        logger.info(f"Database restore 3/4: Dropping '{database}'...")
        if await execute_subprocess_shell(logger, 'dropdb', f'dropdb \'{database}\' --force --if-exists -U postgres') > 0:
            raise Exception(f"Failed to drop database '{database}'!")
        
        logger.info(f"Database restore 4/4: Renaming 'tempdb' -> '{database}'...")
        rename_sql = f'ALTER DATABASE "tempdb" RENAME TO "{database}";'
        if await execute_subprocess_shell(logger, 'psql', f'psql \'postgres\' -U postgres -c \'{rename_sql}\'') > 0:
            raise Exception(f"Failed to rename 'tmpdb' to '{database}'! THIS MEANS NO DATABASE CALLED '{database}' CURRENTLY EXISTS!")
        
        logger.info(f"Successfully restored database from backup '{backup_name}'!")
        return True
    
    except Exception:
        logger.exception(f"RESTORE FAILED! Exception happened during database restore from backup '{backup_name}'!")
        return False
