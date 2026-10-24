# Veyo · Attention Studio

**See what stands out. Make a more informed creative decision.**

Veyo helps you review static ads with predicted visual attention. Upload a
creative, mark the elements that matter, and compare revisions using real
[DeepGaze IIE](https://github.com/matthias-k/DeepGaze) inference and saved evidence.

Built with React, TypeScript, and FastAPI. Designed in
[Figma](https://www.figma.com/design/gxDTce6luov9uIGO95ehO4?node-id=2-2).
One Docker container, persistent files, no SQL database.

## What you can do

- **Organize creatives.** Upload PNGs and JPEGs, search your library, rename or
  archive projects, and explore three original example ads.
- **Mark what matters.** Draw up to eight targets for products, headlines,
  logos, or calls to action, with labels and priorities.
- **Explore attention.** View aligned heatmaps, target attention shares,
  attention relative to image area, and competing regions outside your targets.
- **Compare ideas.** Upload a revision or adjust brightness, contrast,
  saturation, and sharpness across the image or within a selected target.
- **Keep the evidence.** Revisit saved analyses, compare corresponding elements,
  and download creatives, heatmaps, JSON reports, or a complete project ZIP.
- **Return to your workspace.** Back up and restore your browser-held workspace
  key from Settings.

## Quick start

Install Docker with Compose and start its engine. Run from the repository root:

```sh
docker compose up --build -d --wait
```

Open **[localhost:8000](http://127.0.0.1:8000)**.

The container serves the interface, API, and CPU model together. The first build
downloads dependencies and pretrained weights; allow roughly 2 GB of image
storage and 8 GiB of available runtime RAM. Weights are included in the image,
so analysis requests do not download them. No cloud account is needed.

To stop the app:

```sh
docker compose down
```

Projects and images stay in the `creative_files` volume across restarts and
container replacement. Adding `--volumes` deletes that data.

## Your first review

1. **Bring a creative.** Choose an example or upload a PNG or JPEG.
2. **Mark your targets.** Draw around important elements, name them, and confirm
   their bounds.
3. **Run analysis.** Explore the heatmap, target metrics, and competing regions.
4. **Try a revision.** Upload another version or make a controlled adjustment.
   Review its targets, analyze it, and compare the changes side by side.

Keep corresponding target labels and roles consistent between revisions. Each
revision has its own annotations, and saved analyses retain their target snapshots.

## Development

Use **Python 3.12**, **Node 24 LTS**, and Git. Install dependencies from the
repository root:

```sh
python3.12 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements-web-lock.txt
npm ci
```

Start the API in one terminal:

```sh
npm run api
```

Start Vite in another:

```sh
npm run dev
```

Open **[localhost:5173](http://127.0.0.1:5173)**. Vite forwards `/api` requests
to port 8000. The first analysis downloads and loads the pretrained weights into
`model-cache/`; later analyses reuse the loaded model.

To serve the production build without Docker, stop the development API and run
`npm start`. This builds React and serves the interface and API at port 8000.
Stop the Docker app first if it is using that port.

Configuration is optional. See [.env.example](.env.example) for environment
variables to set in the API process.

## Verification

From the repository root, with development dependencies installed:

```sh
npm run build
npm test
(cd backend && .venv/bin/python -m unittest discover -s tests -v)
```

With the app running at port 8000, exercise the real model through the API:

```sh
backend/.venv/bin/python scripts/smoke_test.py http://127.0.0.1:8000 \
  --output outputs/release-smoke.json
```

The smoke test creates a separate review workspace and checks inference,
adjustments, multipart upload, comparison, overlay dimensions, ZIP export, and
workspace isolation. It needs the Python dependencies above, including when
testing Docker. For Vite, use `http://127.0.0.1:5173` instead.

See [release verification](docs/release-verification.md) for observed results
and verification limits.

## Understanding the results

| Metric             | Meaning                                                                                                |
| ------------------ | ------------------------------------------------------------------------------------------------------ |
| Attention share    | Predicted fixation probability inside a target.                                                        |
| Area share         | Fraction of the image covered by that target.                                                          |
| Relative attention | Attention share divided by area share; 2× means twice the image-average predicted attention per pixel. |

Overlapping targets count once in the combined total. Comparison deltas show
actual increases and decreases in percentage points.

These are spatial predictions from one model. They do not measure human
attention, gaze order, clicks, conversions, or sales. A higher score alone does
not establish a better ad. Review the creative itself and validate important
decisions with people. Model errors are surfaced; Veyo never generates a
substitute heatmap.

## Storage and hosting

Local development stores JSON records, images, and analysis artifacts in
`storage/`. Docker uses the persistent volume mounted at `/app/storage`.

Back up **both your data and your workspace key**. Anyone with the key can
access that workspace; losing it can mean losing access. Project ZIP exports
contain creatives and evidence, but exclude the key. Browser storage is specific
to its origin, so use Settings to restore your key when changing hosts or ports.

**Cloud spending is disabled, and no public site has been deployed.** The image
can run on a container host with HTTPS and persistent storage. An optional paid
Cloud Run path uses private object storage and is blocked by default behind an
explicit spending opt-in. See [the hosting runbook](docs/deployment.md).

User accounts, team permissions, generative image editing, and distributed job
queues are outside this release.

## Project notes

- [Design direction](docs/design.md) — visual foundations and Figma reference.
- [Storage](docs/database.md) — file layout, persistence, and backups.
- [Application architecture](docs/decisions/0006-file-backed-studio.md) — records,
  model lifecycle, and comparisons.
- [Single-container hosting](docs/decisions/0007-single-container.md) — the current
  deployment decision.
- [Build log](docs/build-log.md) — historical project notes.

## Credits

The workflow is inspired by [Pixel](https://github.com/EnesYilmazcode/Pixel).
Attention predictions use [DeepGaze IIE](https://github.com/matthias-k/DeepGaze),
by Linardos, Kümmerer, Press, and Bethge. Veyo does not develop or train that model.
Third-party dependency notices are included in
[THIRD-PARTY.txt](frontend/public/licenses/THIRD-PARTY.txt) and served at
`/licenses/THIRD-PARTY.txt` in the app.
