#!/usr/bin/env bash
# Optional paid Cloud Run deployment. Local Docker is the default, no-cost path.
set -euo pipefail
if [[ "${VEYO_ALLOW_PAID_CLOUD:-}" != "I_ACCEPT_USAGE_BASED_CHARGES" ]]; then
  echo 'Cloud spending is disabled for Veyo. Use docker compose up --build -d --wait locally.' >&2
  echo 'Paid deployment requires a new spending decision and explicit VEYO_ALLOW_PAID_CLOUD opt-in.' >&2
  exit 2
fi
PROJECT_ID="${1:?Usage: bash scripts/deploy.sh GOOGLE_CLOUD_PROJECT_ID}"
REGION=us-central1
BUCKET="${PROJECT_ID}-veyo-files"
RUNTIME="veyo-runtime@${PROJECT_ID}.iam.gserviceaccount.com"
BUILDER="veyo-builder@${PROJECT_ID}.iam.gserviceaccount.com"
BUILD_BUCKET="${PROJECT_ID}-veyo-build-source"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
if ! command -v gcloud >/dev/null && [[ -x "$ROOT_DIR/.local/google-cloud-sdk/bin/gcloud" ]]; then
  export PATH="$ROOT_DIR/.local/google-cloud-sdk/bin:$PATH"
  export CLOUDSDK_PYTHON="${CLOUDSDK_PYTHON:-$ROOT_DIR/backend/.venv/bin/python}"
fi
command -v gcloud >/dev/null || { echo 'Install the Google Cloud CLI and run gcloud auth login.' >&2; exit 2; }
if [[ "$(gcloud billing projects describe "$PROJECT_ID" --format='value(billingEnabled)')" != "True" ]]; then
  echo "Link a billing account to $PROJECT_ID before deploying the inference service." >&2
  exit 2
fi
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com storage.googleapis.com iam.googleapis.com serviceusage.googleapis.com --project "$PROJECT_ID"
gcloud artifacts repositories describe veyo --location "$REGION" --project "$PROJECT_ID" >/dev/null 2>&1 || \
  gcloud artifacts repositories create veyo --repository-format docker --location "$REGION" --project "$PROJECT_ID"
gcloud storage buckets describe "gs://$BUCKET" --project "$PROJECT_ID" >/dev/null 2>&1 || \
  gcloud storage buckets create "gs://$BUCKET" --location "$REGION" --uniform-bucket-level-access --public-access-prevention --project "$PROJECT_ID"
gcloud iam service-accounts describe "$RUNTIME" --project "$PROJECT_ID" >/dev/null 2>&1 || \
  gcloud iam service-accounts create veyo-runtime --display-name 'Veyo file storage runtime' --project "$PROJECT_ID"
gcloud storage buckets add-iam-policy-binding "gs://$BUCKET" --member "serviceAccount:$RUNTIME" --role roles/storage.objectUser --project "$PROJECT_ID" >/dev/null
gcloud storage buckets describe "gs://$BUILD_BUCKET" --project "$PROJECT_ID" >/dev/null 2>&1 || \
  gcloud storage buckets create "gs://$BUILD_BUCKET" --location "$REGION" --uniform-bucket-level-access --public-access-prevention --project "$PROJECT_ID"
gcloud iam service-accounts describe "$BUILDER" --project "$PROJECT_ID" >/dev/null 2>&1 || \
  gcloud iam service-accounts create veyo-builder --display-name 'Veyo container build' --project "$PROJECT_ID"
gcloud artifacts repositories add-iam-policy-binding veyo --location "$REGION" --member "serviceAccount:$BUILDER" --role roles/artifactregistry.writer --project "$PROJECT_ID" >/dev/null
gcloud storage buckets add-iam-policy-binding "gs://$BUILD_BUCKET" --member "serviceAccount:$BUILDER" --role roles/storage.objectViewer --project "$PROJECT_ID" >/dev/null
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member "serviceAccount:$BUILDER" --role roles/logging.logWriter >/dev/null
BUILD_ID="$(gcloud builds submit --config cloudbuild.yaml --project "$PROJECT_ID" --async \
  --service-account "projects/$PROJECT_ID/serviceAccounts/$BUILDER" \
  --gcs-source-staging-dir "gs://$BUILD_BUCKET/source" --format='value(id)')"
gcloud builds describe "$BUILD_ID" --project "$PROJECT_ID" --format='value(logUrl)'
# Stable `builds log --stream` only follows Cloud Storage logs. This build writes
# to Cloud Logging, so wait on the build status itself before deploying its image.
build_deadline="$(( $(date +%s) + 2100 ))"
previous_status=""
while true; do
  build_status="$(gcloud builds describe "$BUILD_ID" --project "$PROJECT_ID" --format='value(status)')"
  if [[ "$build_status" != "$previous_status" ]]; then
    echo "Container build $BUILD_ID: $build_status"
    previous_status="$build_status"
  fi
  case "$build_status" in
    SUCCESS) break ;;
    FAILURE|INTERNAL_ERROR|TIMEOUT|CANCELLED|EXPIRED)
      echo "Container build failed; deployment stopped." >&2
      exit 1 ;;
  esac
  if [[ "$(date +%s)" -ge "$build_deadline" ]]; then
    echo "Stopped waiting for build $BUILD_ID; inspect its status before continuing." >&2
    exit 1
  fi
  sleep 10
done
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/veyo/api:${BUILD_ID}"
gcloud run deploy veyo-api --image "$IMAGE" --project "$PROJECT_ID" --region "$REGION" \
  --service-account "$RUNTIME" --allow-unauthenticated --cpu 2 --memory 8Gi \
  --concurrency 8 --max-instances 1 --min-instances 0 --timeout 60 --port 8080 \
  --set-env-vars "VEYO_GCS_BUCKET=$BUCKET,VEYO_THREADS=2"
gcloud run services describe veyo-api --project "$PROJECT_ID" --region "$REGION" --format='value(status.url)'
