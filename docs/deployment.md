# Deploy Veyo to web.app

The complete deployment is a Firebase Hosting frontend, a Cloud Run Python API,
and private Google Cloud Storage files. This requires Firebase and Google Cloud
authentication and a billing-enabled project. Docker Desktop is not required;
Cloud Build builds the container remotely.

The deployment project is `veyo-attention-studio` (Google Cloud project number
`569676285410`). It has already been created; do not create a duplicate. The
repository's `.firebaserc` selects it by default. Both CLIs are authenticated.
Firebase's first-time terms acceptance and a linked billing account are the
remaining account setup requirements before publication.

## Authenticate and create the project

Use Node 24 LTS for the Firebase deployment CLI. Install the
[Google Cloud CLI](https://cloud.google.com/sdk/docs/install-sdk), then sign in:

```sh
npx firebase login
gcloud auth login
```

Choose an available project ID, then create the requested new Firebase project:

```sh
npx firebase projects:create YOUR_PROJECT_ID --display-name 'Veyo Attention Studio'
```

Link the project's billing account in the Google Cloud console before deploying
Cloud Run. This selects the account that pays for compute, builds, image storage,
and file storage. The deployment does not select or link a billing account for you.
Set a Google Cloud billing budget and notifications appropriate to your usage.

## Deploy the verified source

From the repository root:

```sh
bash scripts/deploy.sh YOUR_PROJECT_ID
```

The script enables required APIs, creates the image repository and private buckets,
creates separate build and runtime service accounts, builds the CPU-only image,
verifies the build succeeded, deploys `veyo-api`, builds the frontend, and publishes
Hosting. It can be run again for later revisions. Source upload honors
`.gcloudignore`; Docker build context honors `.dockerignore`.

The runtime account accesses only the creative-files bucket. The build account can
read its build-source bucket, publish to the image repository, and write build logs.
Buckets enforce public access prevention. The public API requires an unguessable
workspace key for all creative resources; health is public.

Firebase rewrites `/api/**` before the SPA fallback, with `pinTag` associating the
frontend deploy with the current API revision. The default Cloud Run service has
two CPUs, 8 GiB memory, one application worker, concurrency eight, at most one
instance, and zero minimum instances. The model itself permits one inference at
a time. A busy response is retryable; there is no distributed job queue.

The HTTPS URL is `https://YOUR_PROJECT_ID.web.app`. Uploaded data remains in the
private bucket when the application scales down or a container is replaced.

## Verify the deployment

```sh
backend/.venv/bin/python scripts/smoke_test.py https://YOUR_PROJECT_ID.web.app
```

This creates an isolated temporary review workspace, runs genuine inference on
two creative versions, uploads a revision, compares targets, checks aligned
overlays and ZIP export, and verifies another workspace cannot read the image.
It does not print workspace credentials. The generated review data remains in
storage and can be removed through an explicitly scoped maintenance operation.

Open the deployed app and verify a user upload, target selection, analysis,
comparison, and export. Confirm `/api/health` returns JSON rather than the SPA.

## Local container alternative

```sh
docker compose up --build -d --wait
npm run dev
```

The container build downloads roughly a gigabyte of public pretrained model
weights. The `creative_files` volume holds user data. `docker compose down`
preserves it; adding `--volumes` deletes it. The prior PostgreSQL volume is not
used or deleted by the current application configuration.

## Current verification limit

The local application and real inference workflow have passed verification.
The Docker image and remote cloud resources must be verified by an authenticated
Cloud Build/deployment. The release is not considered published until Hosting
reports success and the deployed smoke test passes.
