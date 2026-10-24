#!/usr/bin/env bash
# Build and deploy the complete application. Requires an authenticated, billing-enabled project.
set -euo pipefail
PROJECT_ID="${1:?Usage: bash scripts/deploy.sh FIREBASE_PROJECT_ID}"
REGION=us-central1
BUCKET="${PROJECT_ID}-veyo-files"
RUNTIME="veyo-runtime@${PROJECT_ID}.iam.gserviceaccount.com"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
command -v gcloud >/dev/null || { echo 'Install the Google Cloud CLI and run gcloud auth login.' >&2; exit 2; }
if [[ "$(gcloud billing projects describe "$PROJECT_ID" --format='value(billingEnabled)')" != "True" ]]; then
  echo "Link a billing account to $PROJECT_ID before deploying the inference service." >&2
  exit 2
fi
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com storage.googleapis.com --project "$PROJECT_ID"
gcloud artifacts repositories describe veyo --location "$REGION" --project "$PROJECT_ID" >/dev/null 2>&1 || \
  gcloud artifacts repositories create veyo --repository-format docker --location "$REGION" --project "$PROJECT_ID"
gcloud storage buckets describe "gs://$BUCKET" --project "$PROJECT_ID" >/dev/null 2>&1 || \
  gcloud storage buckets create "gs://$BUCKET" --location "$REGION" --uniform-bucket-level-access --public-access-prevention --project "$PROJECT_ID"
gcloud iam service-accounts describe "$RUNTIME" --project "$PROJECT_ID" >/dev/null 2>&1 || \
  gcloud iam service-accounts create veyo-runtime --display-name 'Veyo file storage runtime' --project "$PROJECT_ID"
gcloud storage buckets add-iam-policy-binding "gs://$BUCKET" --member "serviceAccount:$RUNTIME" --role roles/storage.objectUser --project "$PROJECT_ID" >/dev/null
BUILD_ID="$(gcloud builds submit --config cloudbuild.yaml --project "$PROJECT_ID" --format='value(id)')"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/veyo/api:${BUILD_ID}"
gcloud run deploy veyo-api --image "$IMAGE" --project "$PROJECT_ID" --region "$REGION" \
  --service-account "$RUNTIME" --allow-unauthenticated --cpu 2 --memory 8Gi \
  --concurrency 8 --max-instances 1 --min-instances 0 --timeout 60 --port 8080 \
  --set-env-vars "VEYO_GCS_BUCKET=$BUCKET,VEYO_ALLOWED_ORIGINS=https://${PROJECT_ID}.web.app,VEYO_THREADS=2"
npm run build
npx firebase deploy --only hosting --project "$PROJECT_ID" --non-interactive
echo "Deployed: https://${PROJECT_ID}.web.app"
