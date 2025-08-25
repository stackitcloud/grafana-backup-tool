# Stage 1: Build the wheel file
FROM python:3.13-alpine AS builder

WORKDIR /build

ADD . /build

# Build the wheel file
RUN pip install poetry && \
    poetry build && \
    ls -l /build/dist

# Stage 2: Create the final image
FROM python:3.13-alpine

ENV RESTORE=false
ENV ARCHIVE_FILE=""
ENV PY_COLORS=1
ENV TZ=UTC
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /opt/grafana-backup-tool

# Copy the wheel file from the builder stage
COPY --from=builder /build/dist/*.whl /

# Install the wheel file
RUN pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir $(find / -name "grafana_backup-*.whl") && \
    rm -f ansible_doctor-*.whl && \
    chown -R 1337:1337 /opt/grafana-backup-tool && \
    chmod -R 755 /opt/grafana-backup-tool

USER 1337
CMD ["sh", "-c", "if [ \"$RESTORE\" = true ]; then if [ ! -z \"$AWS_S3_BUCKET_NAME\" ] || [ ! -z \"$AZURE_STORAGE_CONTAINER_NAME\" ] || [ ! -z \"$GCS_BUCKET_NAME\" ]; then grafana-backup restore $ARCHIVE_FILE; else grafana-backup restore _OUTPUT_/$ARCHIVE_FILE; fi else grafana-backup save; fi"]
