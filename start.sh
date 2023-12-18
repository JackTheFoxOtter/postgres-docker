# Export current UID and GID to environment variables (used in postgres-container in docker-compose.yaml)
export CURRENT_UID=$(id -u)
export CURRENT_GID=$(id -g)

# Ensure data folders exist and are owned by the executing user.
# These folders get mounted into containers and are used for persistent storage.
# The containers should run as CURRENT_UID and CURRENT_GID, since file permissions
# are copied between containers and host. This way, the owner of the files on the host
# is always the user that started the application.
datafolders=("postgres" "backups" "logs")
for folder in "${datafolders[@]}"; do
    mkdir "./data/$folder"
    chown "$CURRENT_UID:$CURRENT_GID" "./data/$folder"
done

docker compose up --build --build-arg "BUILDDATE=$(date +%s)"