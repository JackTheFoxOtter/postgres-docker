FROM postgres:16-alpine

# Install required packages
RUN apk add --no-cache git python3 py3-pip;

# Install required python packages
# NOTE: The container screams at me if I try to install the packages without a venv.
#       Since this is a container tho, I don't see much harm in passing --break-system-packages.
#       If it works, it works.
ADD api/requirements.txt /api/requirements.txt
RUN pip install -r /api/requirements.txt --break-system-packages;

# Copy remaining application files
COPY api /api
COPY entrypoint.py /entrypoint.py

# Invalidate the cache from here on.
# This prevents docker from caching permissions of mounted directories,
# as those could change on the host at any time.
ARG BUILDDATE
ARG CURRENT_UID
ARG CURRENT_GID
RUN echo ${BUILDDATE} > /etc/builddate; \
    # Set directory permissions
    mkdir -p /backups /logs /var/lib/postgresql/data; \
    chown ${CURRENT_UID}:${CURRENT_GID} /backups /logs /var/lib/postgresql/data;

ENTRYPOINT [ "python", "entrypoint.py" ]