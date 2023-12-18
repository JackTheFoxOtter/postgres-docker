# Creates a backup for a database and stores it in a (gziped) file.
# Path to file will be created if it doesn't already exist.
# Usage: create_backup.sh <dbname> <backup_file_path>
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

# Create path if not exists
backup_file_dir=$(dirname "$backup_file")
if ! [ -d "$backup_file_dir" ]; then
    mkdir -p "$backup_file_dir"
    echo "Created path '${backup_file_dir}'."
fi

# Abort if backup_file already exists
if [ -d "$backup_file" ]; then
    echo "'${backup_file}' is a directory!"
    exit 1
elif [ -f $backup_file ]; then
    echo "File '${backup_file}' already exists!"
    exit 1
fi

echo "Creating backup for database '${dbname}' > '${backup_file}'..."
pg_dump --dbname="$dbname" -U postgres | gzip > "$backup_file"
if ! [ $? -eq 0 ]; then
    echo "Failed to create backup!"
    rm "$backup_file" 2> /dev/null
    if [ $? -eq 0 ]; then
        echo "Removed corrupt backup file '${backup_file}'."
    fi
    exit 1
fi