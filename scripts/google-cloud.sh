#!/usr/bin/env bash
# Prefer an installed CLI; use the ignored project-local official SDK when available.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if command -v gcloud >/dev/null; then
  exec gcloud "$@"
elif [[ -x "$ROOT_DIR/.local/google-cloud-sdk/bin/gcloud" ]]; then
  export CLOUDSDK_PYTHON="${CLOUDSDK_PYTHON:-$ROOT_DIR/backend/.venv/bin/python}"
  exec "$ROOT_DIR/.local/google-cloud-sdk/bin/gcloud" "$@"
else
  echo 'Install the official Google Cloud CLI: https://cloud.google.com/sdk/docs/install-sdk' >&2
  exit 2
fi
