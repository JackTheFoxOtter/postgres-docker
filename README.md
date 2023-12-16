# postgres-docker
Docker container for Postgres with simple Quart API.
The goal of adding the API was providing a simple way for a application to have control over backup / restore functionality of Postgres. This is intended to serve as the baseline database implementation for my projects.

## General Usage
To start the main container, use
> docker compose up

To start the main container together with the PGData container, use
> docker compose up --profile=pgdata

## API Usage
The API currently provides methods to backup and restore the database.

WARNING: The API port should NOT be exposed to the host machine. It has no security measures in place to prevent tampering with the database. It is designed for use only through a non-external docker network, shared only with the app container (and if running the PGAdmin instance).


## Additional Notes
The containers are using directories mounted underneath the ./data directory because I don't like using external Docker volumes. To fix issues with permissions on Linux, the environment variables CURRENT_UID and CURRENT_GID can be set to the corresponding values of the host environment (that is what happens in the start.sh script). This will run the applications in the container with the same user ID as started the containers on the host system, which will own the mounted folders and ensure identical ownership of the mounted directories.