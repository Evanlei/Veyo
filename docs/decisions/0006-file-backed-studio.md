# 0006 — File-backed attention studio

Date: 2026-10-24. Supersedes decision 0005 for the application runtime.

The user requested a complete Pixel-inspired app without PostgreSQL. Veyo now
uses files and JSON objects locally, and the same object interface with Google
Cloud Storage when deployed. No SQL service, tables, or migrations are required.
The old Docker database volume is not removed by this change.

## Records and identity

Projects, creative assets, and analysis runs have independent UUID paths under
`workspaces/<sha256-of-workspace-key>/`. The browser generates a 256-bit key and
sends it in an authorization header. Only its digest appears in storage paths.
Images are separate PNG objects; JSON never embeds base64 images. The Settings
screen lets users back up or restore their key. This is anonymous capability
access, not an account system or team permission model.

Local writes use a same-directory temporary file, fsync, and atomic replacement.
Cloud object replacement is atomic per object. There are no multi-object
transactions: an interrupted upload may leave an unreferenced image, and a
partially written analysis remains incomplete. Run metadata is completed last.
Completed runs retain their own target snapshots, model identity, settings,
input hash, and metric values. Editing current targets does not rewrite history.

## Prediction lifecycle

One real CPU DeepGaze IIE predictor is loaded lazily and reused sequentially.
Overlapping inference returns a retryable busy response. The request remains
open during computation so Cloud Run allocates CPU throughout the work. Model
weights are cached locally and baked into the deployed container image.
No alternate model, generated heatmap, or fabricated result substitutes on error.

A canonical image is EXIF-oriented, composited onto white, and limited to a
1600-pixel longest side. Annotations and model probabilities use that same grid.
The raw uploaded file's hash and original dimensions are retained as provenance.
Prediction caches validate image hash, model identity, map shape, normalization,
and probability-file hash before reuse. Re-scoring new targets can reuse a valid
prediction. Runs left in progress for over 15 minutes are surfaced as interrupted.

## Interpretation

Display attention share, area share, and attention-per-area relative to the whole
image. Union overlapping targets for totals. Compare targets by the combination
of role and case-insensitive label, with independently confirmed geometry on each
revision. Return actual positive and negative changes in percentage points.
Competing region boxes lie outside the marked targets; they have geometric names
instead of invented semantic descriptions.

Controlled adjustments preserve dimensions, create a new revision, and record
their settings and changed-pixel evidence. Local adjustments leave pixels outside
the selected region unchanged. Generative image editing is outside this release.

## Deployment and tradeoffs

Decision [0007](0007-single-container.md) updates the hosting architecture:
one container serves React, FastAPI, and the model, with a persistent local file
volume. The optional paid Cloud Run adapter uses private GCS objects to survive
container replacement. It uses one instance, one worker, two CPUs, and 8 GiB RAM.
Write requests are bounded per connection in process, and upload bytes and decoded
pixels are limited. These bounds are not a distributed abuse-prevention system.

Listing scans JSON objects. Mutable project names and current annotations use
last-write-wins semantics; simultaneous editors can overwrite those fields.
SQLite/Postgres, account-based access, pagination, and a durable distributed job
queue become appropriate when collaborative scale requires them. A second model
or human validation is needed to establish more than single-model saliency gains.
