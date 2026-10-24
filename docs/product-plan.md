# Veyo Attention Studio

Build a complete, deployable static-creative review tool inspired by Pixel.

## Release scope

- Creative library with upload, search, rename, archive, and sample projects.
- Canonical image preview with multiple named, goal-specific rectangle targets.
- Real DeepGaze IIE analysis, aligned heatmaps, area-adjusted attention metrics,
  competing regions, and explicit model status.
- Immutable analysis history, revision uploads, and side-by-side comparison.
- Controlled image adjustments with before/after analysis and change evidence.
- Downloadable creative, overlay, JSON report, and portable project export.
- Responsive, keyboard-accessible React/TypeScript interface designed in Figma.
- FastAPI API, bounded CPU inference, filesystem/JSON persistence; no SQL service.
- Firebase Hosting frontend and containerized Python backend deployment path.

## Product rules

Scores are model predictions, never CTR or sales estimates. No fallback heatmaps.
Each revision owns its annotations. Keep losing revisions and actual deltas.
Persist original files separately from metadata; publish records atomically.
Anonymous workspaces isolate projects using an unguessable browser-held key.
Uploaded creatives are private application data, never committed automatically.

## Design direction

Manrope typography, warm ivory surfaces, ink text, fine borders, cobalt actions,
and spacious image-led layouts. Use Figma to establish composition and tokens.
Make the creative and its evidence the focal points.

## Delivery

Work on `feat/attention-studio` with frequent scoped commits. The repository
started this session with seven commits; target at least 100 total commits.
Verify the real upload → annotation → inference → save → compare → export flow.
Cloud deployment requires an authenticated Firebase project and a Python host;
never claim a recorded sample is live inference.
