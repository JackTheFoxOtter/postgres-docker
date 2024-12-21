CONTAINER_UID=${CONTAINER_UID:-1000}
CONTAINER_GID=${CONTAINER_GID:-1000}

init_directory () {
    # Ensures the specified directory exists and is owned by the correct user
    mkdir "$1"
    chown "$CONTAINER_UID:$CONTAINER_GID" "$1"
}

# Initialize required directories
init_directory '/var/lib/postgresql/data'
init_directory '/backups'
init_directory '/logs'
init_directory '/var/lib/pgadmin'
