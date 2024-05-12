from source.modules.utils import execute_subprocess_shell, get_timestamped_filename, get_unique_filename
from source.env import PATH_BACKUPS
from typing import List, Tuple
import logging
import os


logger = logging.getLogger('database_backup')


def get_backups() -> List[str]:
    logger.debug(f"Fetching backup file list...")
    return [ path for path in os.listdir(PATH_BACKUPS) ]


async def try_create_backup(database : str, backup_name : str) -> Tuple[bool, str]:
    logger.info(f"Attempting to create backup '{backup_name}' for database '{database}'...")
    try:
        backup_file_name = get_unique_filename(PATH_BACKUPS, get_timestamped_filename(f"{database}_{backup_name}", f"postgresql.gz"))
        backup_file_path = os.path.join(PATH_BACKUPS, backup_file_name)
        if await execute_subprocess_shell(logger, 'create_backup', f'/api/scripts/create_backup.sh "{database}" "{backup_file_path}"') > 0:
            raise Exception("Failed to create backup!")

        logger.info(f"Successfully backed up database '{database}'! (-> '{backup_file_path}')")
        return True, backup_file_name
    
    except Exception:
        logger.exception(f"BACKUP FAILED! Exception happened during database backup '{backup_name}'!")
        return False, ""


async def try_restore_backup(database : str, backup_file_name : str) -> bool:
    logger.info(f"Attempting to restore backup from file '{backup_file_name}' for database '{database}'...")
    try:
        backup_file_path = os.path.join(PATH_BACKUPS, backup_file_name)
        if await execute_subprocess_shell(logger, 'restore_backup', f'/api/scripts/restore_backup.sh "{database}" "{backup_file_path}"') > 0:
            raise Exception("Failed to restore backup!")
        
        logger.info(f"Successfully restored database from backup '{backup_file_path}'!")
        return True
    
    except Exception:
        logger.exception(f"RESTORE FAILED! Exception happened during database restore from backup file '{backup_file_name}'!")
        return False
