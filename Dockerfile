FROM postgres:16-alpine

# Install required packages
RUN apk add --no-cache \
    python3 \
    py3-pip

# Install required python packages
COPY api /api
RUN pip install -r /api/requirements.txt

# Expose port 5000 for the API
EXPOSE 5000

# Entrypoint
COPY entrypoint.py /entrypoint.py
ENTRYPOINT [ "python", "entrypoint.py" ]