FROM postgres:16-alpine

# Build args
ARG CURRENT_UID
ARG CURRENT_GID

# Install required packages
RUN apk add --no-cache \
    python3 \
    py3-pip

# Install required python packages
COPY api /api
# NOTE: The container screams at me if I try to install the packages without a venv.
#       Since this is a container tho, I don't see much harm in passing --break-system-packages.
#       If it works, it works.
RUN pip install -r /api/requirements.txt --break-system-packages

# Prepare backup and log folder permissions
RUN mkdir -p /backups /logs /var/lib/postgresql/data
RUN chown ${CURRENT_UID}:${CURRENT_GID} /backups /logs /var/lib/postgresql/data

# Expose port 5000 for the API
EXPOSE 5000

# Entrypoint
COPY entrypoint.py /entrypoint.py
CMD exec python entrypoint.py 2>&1 | tee -a "/logs/$(date +'%Y%m%d%H%M%S')_postgres.log"