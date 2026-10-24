# Run and host Veyo

**Public demo: [veyo-attention-studio.web.app](https://veyo-attention-studio.web.app).**
It serves three fictional sample ads and six genuine saved DeepGaze analyses,
including original/revision comparisons and PNG, JSON, and ZIP downloads.
Persistent labels explain that results are recorded. Uploads, drawing targets,
adjustments, and new inference are available in the full local application.

Cloud spending remains disabled. Firebase Hosting serves only static files;
there are no public API, Cloud Run, Functions, or database services. Project
`veyo-attention-studio` (`569676285410`) has no linked billing account, verified
after publication on 2026-10-24. This is a demonstration of saved evidence, not
free hosted model compute.

## Build and preview the recorded demo

With Node 24 and repository dependencies installed (`npm ci`):

```sh
npm run build:demo
npm run preview:demo
```

Open the printed local URL. The build validates every recording and artifact
hash, then emits `frontend/demo-dist`. Ordinary `npm run build` still produces
the full interface in `frontend/dist`; it is not the static publication artifact.
Demo mode blocks mutations before network access and creates no workspace key.

The manifest and all public artifacts live in `frontend/public/demo/`. To
regenerate them with the backend environment installed:

```sh
backend/.venv/bin/python scripts/record_demo.py
npm run build:demo
```

The recorder uses an isolated temporary workspace and only repository sample
ads. It makes controlled 1.20× brightness revisions and runs the production
analysis service, retaining both gains and losses. Validated matching README
predictions can be reused; otherwise it runs real CPU inference. Public IDs
are stable, and image hashes, model identity, and artifact hashes are retained.
No uploaded user creatives or workspace credentials are published.

## Publish the static demo

Authenticate Firebase CLI and Google Cloud CLI under the owner's account. The
Cloud CLI is used only to check billing, not to create cloud compute:

```sh
npx --yes firebase-tools@15.34.1 login
npm run cloud -- auth login
npm run deploy:demo
```

The deploy script refuses to continue unless billing is disabled. It verifies
that `firebase.json` publishes only `frontend/demo-dist` with static SPA rewrites,
validates and builds the recording, then deploys only Firebase Hosting. It never
enables billing. Firebase terms must already be accepted by the account owner.
The project must remain on its free hosting allowance; this script does not
upgrade its plan. HTML revalidates, hashed assets are immutable, and recordings
use `no-store` to avoid mixing versions. Unknown API and asset paths return 404.

Verify a release independently over HTTPS:

```sh
backend/.venv/bin/python scripts/check_public_demo.py --output outputs/public-demo-verification.json
```

This checks all 27 artifact hashes, image dimensions, ZIP contents, direct links,
cache/security headers, model identity, and missing-resource responses. Inspect
the deployed interface in a browser as well; HTTP checks do not verify layout.

## Full application

Veyo also ships as one Docker image. FastAPI serves the compiled React interface,
the `/api` routes, and CPU DeepGaze IIE inference on port 8080. All browser
requests use the same origin. No separate frontend host or database is needed.

## Local Docker

With Docker Desktop running:

```sh
docker compose up --build -d --wait
```

Open **http://127.0.0.1:8000**. There is no second development server to start.
Compose binds the host port to loopback and mounts `creative_files` at
`/app/storage`. Model weights are downloaded during the build and baked into
the image, so inference requests do not need to download them. The first build
is large; allow roughly 2 GB of image storage and 8 GiB of available runtime RAM.
The service runs as nonroot user 10001 with one Python worker.

```sh
docker compose logs --tail 50 app
docker compose down
```

Stopping or replacing the container preserves the volume. `down --volumes`
deletes it. Back up both the volume and the browser's workspace key from Settings;
a lost key cannot be reconstructed from the stored hash. The older PostgreSQL
volume is unused and has not been deleted.

Without Docker, install the dependencies described in the README and run
`npm start`. This builds the frontend and serves it with the API at port 8000.
`VEYO_FRONTEND_DIR` can override the default `frontend/dist` directory.

## Verify the running image

```sh
backend/.venv/bin/python scripts/smoke_test.py http://127.0.0.1:8000
```

This runs genuine inference on two revisions, multipart upload, target matching,
comparison, overlay checks, export, and workspace isolation. It creates review
data in an isolated workspace without printing credentials. Open `/guide` and
refresh it to verify the interface's deep links. `/api/health` and unknown API
paths must return JSON, and missing JavaScript must return 404.

## Requirements for a future public host

Run this image on a container host with HTTPS, at least two CPU cores, enough
RAM for the model (the provided configuration reserves 8 GiB), and persistent
storage mounted at `/app/storage`. Start with one instance and one worker;
inference is serialized and concurrent analysis returns a retryable busy response.
The default storage uses atomic local file replacement and JSON objects.

Anonymous workspace keys control access to creative resources. Health is public.
The in-process write limiter and body limits are modest abuse bounds; public
exposure needs host-level request controls appropriate to expected traffic.
Protect stored files and retain backups. Do not use an ephemeral disk for live
creative data or scale local storage across independent replicas.

## Optional Cloud Run deployment — paid, disabled by default

`scripts/deploy.sh` is an optional Google Cloud deployment path, not the default
run command. It exits before calling any cloud CLI unless
`VEYO_ALLOW_PAID_CLOUD` is explicitly set to `I_ACCEPT_USAGE_BASED_CHARGES`.
Do not set that value under the current no-spending decision.

If the owner later authorizes usage-based charges, this path requires Google
Cloud CLI authentication, an existing project, and linked billing. It enables
APIs, provisions private creative and build-source buckets, an image repository,
and separate build/runtime service accounts. Cloud Build builds the complete
image, and Cloud Run serves the entire app at its generated HTTPS service URL.
Firebase terms, Firebase Hosting, and a `web.app` domain are not required.

The runtime account accesses the private creative bucket through the existing
GCS adapter. The build account reads staged source, writes image artifacts and
logs. Cloud Run uses two CPUs, 8 GiB RAM, concurrency eight, at most one instance,
zero minimum instances, and a 60-second request timeout. Scaling to zero does
not eliminate image, build, or object-storage charges. This remote path still
requires authenticated deployment and a successful live smoke test before it
can be called verified. Source upload honors `.gcloudignore`.
