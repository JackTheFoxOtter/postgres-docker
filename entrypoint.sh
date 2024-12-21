#!/bin/sh

# Run initialization script (create & own folders)
/app/scripts/initialize.sh

# Run python app as non-privileged user
exec su -c "python /app/entrypoint.py" appuser
