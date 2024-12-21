# Build the container & inject current date as the build arg
docker compose build --build-arg "BUILDDATE=$(date '+%Y-%m-%d %H:%M:%S')" "$@"
