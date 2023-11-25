FROM postgres:16-alpine

# Install required packages
RUN apk add python3 py3-pip

# Install required python packages
COPY api /api
RUN pip install -r /api/requirements.txt

# Copy s6-overlay files to container
ARG S6_OVERLAY_VERSION=3.1.6.0
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz

# Copy s6 service files to container
COPY services.d /etc/services.d

# Expose port 5000 for the API
EXPOSE 5000

# Start s6-overlay
ENTRYPOINT ["/init"]