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

# Invalidate the cache from here on.
# This prevents docker from caching permissions of mounted directories,
# as those could change on the host at any time.
ARG BUILDDATE
RUN echo ${BUILDDATE} > /etc/builddate

# Set directory permissions
RUN mkdir -p /backups /logs /var/lib/postgresql/data
RUN chown ${CURRENT_UID}:${CURRENT_GID} /backups /logs /var/lib/postgresql/data

# Entrypoint
COPY entrypoint.py /entrypoint.py
ENTRYPOINT [ "python", "entrypoint.py" ]