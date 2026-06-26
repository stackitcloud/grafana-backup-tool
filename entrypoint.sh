#!/bin/bash
set -e

if [ $# -gt 0 ]; then
  if [[ "$1" == -* ]] || [[ "$1" == "save" ]] || [[ "$1" == "restore" ]]; then
    exec grafana-backup "$@"
  fi
  exec "$@"
fi

if [ "$RESTORE" = "true" ]; then
  if [ -n "$AWS_S3_BUCKET_NAME" ] || [ -n "$AZURE_STORAGE_CONTAINER_NAME" ] || [ -n "$GCS_BUCKET_NAME" ]; then
    exec grafana-backup restore "$ARCHIVE_FILE"
  else
    exec grafana-backup restore "_OUTPUT_/$ARCHIVE_FILE"
  fi
else
  exec grafana-backup save
fi
