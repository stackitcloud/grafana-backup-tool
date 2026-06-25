# Stage 1: Build the wheel file
FROM docker.io/python:3.14-alpine@sha256:26730869004e2b9c4b9ad09cab8625e81d256d1ce97e72df5520e806b1709f92 AS builder

WORKDIR /build

ADD . /build

# Build the wheel file
RUN pip install poetry && \
    poetry build && \
    ls -l /build/dist

# Stage 2: Create the final image
FROM docker.io/python:3.14-alpine@sha256:26730869004e2b9c4b9ad09cab8625e81d256d1ce97e72df5520e806b1709f92

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
    rm -f grafana_backup-*.whl && \
    chown -R 1337:1337 /opt/grafana-backup-tool && \
    chmod -R 755 /opt/grafana-backup-tool

USER 1337
CMD ["sh", "-c", "if [ \"$RESTORE\" = true ]; then if [ ! -z \"$AWS_S3_BUCKET_NAME\" ] || [ ! -z \"$AZURE_STORAGE_CONTAINER_NAME\" ] || [ ! -z \"$GCS_BUCKET_NAME\" ]; then grafana-backup restore $ARCHIVE_FILE; else grafana-backup restore _OUTPUT_/$ARCHIVE_FILE; fi else grafana-backup save; fi"]
