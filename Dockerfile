FROM postgres:16-alpine

USER root

# Create appuser and appgroup
ARG CONTAINER_UID
ARG CONTAINER_GID
RUN addgroup --gid $CONTAINER_GID appgroup && \ 
    adduser --uid $CONTAINER_UID --disabled-password --ingroup appgroup appuser

# Install required packages
RUN apk add --no-cache git python3 py3-pip;

# Install required python packages
# NOTE: The container screams at me if I try to install the packages without a venv.
#       Since this is a container tho, I don't see much harm in passing --break-system-packages.
#       If it works, it works.
ADD api/requirements.txt /app/api/requirements.txt
RUN pip install -r /app/api/requirements.txt --break-system-packages;

# Copy remaining application files
COPY . /app

# Allow scripts to be executed
RUN chmod -R +x /app/api/scripts/ /app/scripts /app/entrypoint.sh

# Write builddate to container (this also invalidates the cache from here on)
ARG BUILDDATE
RUN echo $BUILDDATE > /etc/builddate;

ENTRYPOINT [ "/bin/sh", "/app/entrypoint.sh" ]
