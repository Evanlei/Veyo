# Veyo — Attention Studio

See what stands out in your creative before deciding what to change.

Veyo is a complete local web application for reviewing static advertisements:
upload a creative, mark its important elements, run real DeepGaze IIE inference,
and compare revisions using saved, reproducible evidence.

## What is implemented

- Searchable creative library with rename, archive, and original example ads.
- PNG/JPEG uploads with orientation, transparency handling, and bounded dimensions.
- Up to eight named rectangle targets with product/headline/logo/CTA roles and priorities.
- Aligned heatmaps, attention share, area share, and attention relative to image area.
- Competing attention regions outside the marked targets.
- Immutable analysis history, cached predictions, and independent revision annotations.
- Controlled whole-image or localized brightness, contrast, saturation, and sharpness edits.
- Side-by-side revision comparisons with actual positive and negative changes.
- Creative, heatmap, JSON report, and complete-project ZIP downloads.
- Anonymous private workspaces with key backup and restore.
- React/TypeScript frontend designed in [Figma](https://www.figma.com/design/gxDTce6luov9uIGO95ehO4?node-id=2-2).
- FastAPI backend, local files/JSON or private Google Cloud Storage; no SQL database.

Generative image editing, user accounts, team permissions, and distributed job
queues are outside this release. The app never substitutes fabricated predictions
when the model fails.

## Run the complete app in Docker

```sh
docker compose up --build -d --wait
```

Open **http://127.0.0.1:8000**. One container serves the React interface, API,
and real CPU inference. The build includes the frontend and pretrained model
weights. Projects and images persist in the `creative_files` volume across
container replacement. No database or Firebase account is required.

`docker compose down` stops the app and preserves its data. Do not add
`--volumes` unless you intend to delete that data. Keep your workspace key too.

## Develop locally

Use Python 3.12 and Node 24 LTS. From the repository root, create the backend
environment if it does not already exist:

```sh
python3.12 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements-web-lock.txt
npm ci
```

Start the API:

```sh
npm run api
```

In another terminal, start the interface:

```sh
npm run dev
```

Open **http://127.0.0.1:5173**. Vite forwards API requests to port 8000.
For the production interface on one port without Docker, stop the development
API first and run `npm start`; open **http://127.0.0.1:8000**.
The first local inference loads pretrained weights into the ignored model cache;
subsequent predictions reuse the loaded CPU model. The supplied example creatives
are original illustrated ads; their heatmaps are computed when requested.

Local data lives in ignored `storage/`. Back up the workspace key from Settings
to restore access from another browser. A project ZIP contains its creatives and
evidence, not its private access key.

## Verify

```sh
npm run build
npm test
cd backend
.venv/bin/python -m unittest discover -s tests -v
```

With both development servers running, exercise the complete real-model flow
from the repository root:

```sh
backend/.venv/bin/python scripts/smoke_test.py --output outputs/release-smoke.json
```

The smoke test checks real inference, adjustment, multipart upload, corresponding
targets, comparison, overlay dimensions, ZIP contents, and workspace isolation.
See [release verification](docs/release-verification.md) for observed results and
the limits of what has been verified.

## Hosting

Cloud spending is disabled by the project owner's choice. The local container
requires no cloud resources. Veyo has not been published to a public URL.

The same image can run on a container host with a persistent `/app/storage`
volume and HTTPS. Firebase Hosting is not part of the architecture. An optional
Cloud Run deployment script remains available behind an explicit paid-deployment
guard; it uses private object storage because Cloud Run disks are ephemeral.
Read [the deployment runbook](docs/deployment.md) for requirements and limits.

## Reading the results

Attention share is model-predicted fixation probability inside a target. It is
not a percentage of viewers, click probability, CTR, sales, or measured human
attention. Relative attention divides that share by the region's area share.
Overlapping regions count once in the combined total.

DeepGaze IIE predicts spatial saliency rather than temporal gaze paths. Scores
do not establish whether a creative communicates effectively or meets campaign
goals. Each revision needs a correctly placed corresponding target. Review the
actual design and validate consequential decisions with people.

## Architecture and attribution

See [storage](docs/database.md), [the architecture decision](docs/decisions/0006-file-backed-studio.md),
[design direction](docs/design.md), and the historical [build log](docs/build-log.md).

The workflow is inspired by [Pixel](https://github.com/EnesYilmazcode/Pixel).
Predictions use [DeepGaze IIE](https://github.com/matthias-k/DeepGaze), by Linardos,
Kümmerer, Press, and Bethge. Veyo does not claim to have developed or trained that
model. Dependency notices ship in `/licenses/THIRD-PARTY.txt`.
