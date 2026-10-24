# Run and host Veyo

Veyo ships as one Docker image. FastAPI serves the compiled React interface,
the `/api` routes, and CPU DeepGaze IIE inference on port 8080. All browser
requests use the same origin. No separate frontend host or database is needed.

**Current decision: keep cloud spending disabled.** No public deployment has
been made. The existing Google Cloud project `veyo-attention-studio`
(`569676285410`) was created during earlier setup; billing was disabled at the
last account check. No paid cloud resources were provisioned. Removing the
Firebase configuration from this repository does not delete that project or
change account authentication.

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
