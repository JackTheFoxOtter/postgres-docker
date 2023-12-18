# Restores a database from a (gziped) backup file.
# WARNING: dbname cannot be a connection string!
# Usage: restore_backup.sh <dbname> <backup_file_path>
#! bin/bash
set -o pipefail

dbname=$1
backup_file=$2

# Check if arguments were provided
if [ -z "$dbname" ]; then
    echo "No dbname provided! (First argument)"
    exit 1
elif [ -z "$backup_file" ]; then
    echo "No backup file provided! (Second argument)"
    exit 1
fi
 
# Abort if backup_file doesn't exists
if ! [ -f "$backup_file" ]; then
    echo "Backup file '${backup_file}' doesn't exist!"
    exit 1
fi

echo "Database restore 1/5: Dropping temporary database 'tempdb' if exists..."
dropdb "tempdb" --force --if-exists -U "postgres"
if ! [ $? -eq 0 ]; then
    echo "Failed to drop temporary database 'tempdb'!"
    exit 1
fi

echo "Database restore 2/5: Creating temporary database 'tempdb'..."
createdb "tempdb" -U "postgres"
if ! [ $? -eq 0 ]; then
    echo "Failed to create temporary database 'tempdb'!"
    exit 1
fi

echo "Database restore 3/5: Populating 'tempdb' from backup file '${backup_file}'..."
gunzip < "$backup_file" | psql "tempdb" -U "postgres"
if ! [ $? -eq 0 ]; then
    echo "Failed to populate temporary database 'tempdb' from backup file '${backup_file}'! (Is the file corrupt?)"
    exit 1
fi

echo "Database restore 4/5: Dropping '${dbname}' if exists..."
dropdb "${dbname}" --force --if-exists -U "postgres"
if ! [ $? -eq 0 ]; then
    echo "Failed to drop database '${dbname}'!"
    exit 1
fi

echo "Database restore 5/5: Renaming 'tempdb' -> '${dbname}'..."
psql "postgres" -c "ALTER DATABASE \"tempdb\" RENAME TO \"${dbname}\"" -U "postgres"
if ! [ $? -eq 0 ]; then
    echo "Failed to rename database 'tmpdb' to '${dbname}'! THIS MEANS NO DATABASE CALLED '${dbname}' CURRENTLY EXISTS!"
    exit 1
fi