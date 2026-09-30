# Build log

## 2026-09-29 — Model experiment environment

Completed one increment: a fresh, isolated Python environment with resolved dependencies. No prior experiment code, dependency pins, installed environment, sample images or model weights were copied.

### Changes and choices

- Created `backend/.venv` using the available Python 3.12.14 runtime. The environment is ignored by Git.
- Added `backend/requirements.in` for direct dependencies and `backend/requirements.txt` for the exact installed snapshot.
- Resolved DeepGaze and CLIP source commits from their upstream repositories during setup. Included dependencies needed by the current package imports without changing upstream code.
- Added setup instructions and decision 0001 describing isolation, source pins and portability limits.
- The first sample is The Ordinary JPEG; the user chose all four products as the target before inference. Exact target boundaries still need to be marked.

### Verification

- `python -m pip check`: no broken requirements.
- Confirmed the interpreter is Python 3.12 inside Veyo's environment.
- Imported `DeepGazeIIE` successfully without instantiating a model.
- Executed a basic PyTorch CPU tensor operation.
- Decoded the actual supplied JPEG, confirming RGB data with shape `(1024, 683, 3)` after orientation handling. The original file was not modified.
- Verified `.venv` and the sample remain ignored; dependency files and documentation are trackable.

Resolved core package versions:

- torch: 2.14.0
- torchvision: 0.29.0
- numpy: 2.5.3
- Pillow: 12.3.0
- deepgaze_pytorch: 1.2.1
- clip: 1.0

### Tradeoffs and limits

The version snapshot was verified on macOS ARM/Python 3.12, not Linux or CUDA. The initial virtual environment depends on the bundled base Python installation; the setup guide explains how to recreate it with standalone Python 3.12. No model weights were downloaded, no inference was run, and no app feature is implemented by this setup.

### Learning checkpoint and next increment

Activate the environment in the VS Code terminal and check `python --version`. Understand that `.venv` contains replaceable local installations, while the requirements files belong in Git so the installation can be recreated.

Next: walk through the image-to-tensor and log-probability contracts, mark the product target, and build the first real DeepGaze experiment. Do not claim a dependency import verifies model loading or prediction correctness.

## 2026-09-30 — Canonical image loader

Completed `veyo.images.load_image`: content-based PNG/JPEG validation, animation rejection, EXIF orientation, RGBA compositing onto white, and an independent RGB return value. Fixed the incomplete copy expression in the user's starter. Source files remain unchanged and dimensions are preserved after orientation.

Added eleven focused checks using Python's built-in unittest; no dependency changes. Tests cover opaque pixel preservation, transparency and palette handling, rotated/mirrored coordinates, detached image data, unsupported or disguised formats, animation, invalid/truncated images and missing files. The supplied JPEG is also checked directly; no model prediction is part of this increment.

Choice and tradeoff: white follows the user's selected display background; it makes transparency deterministic but means results apply to that background. Using RGBA for all inputs keeps one compositing path at the cost of temporary image buffers. The next feature remains real inference and a manually verified product target; the heatmap must use the same canonical image coordinates.

Git staging, commits and pushes are left to the user. Suggested commit message: `feat: add validated RGB image loader`.

## 2026-09-30 — Real DeepGaze IIE inference

Added `veyo.inference` with a reusable sequential CPU predictor and a command-line entry point. The canonical image becomes a 1 x 3 x H x W float32 tensor with RGB values in 0..255. Predictions are validated as finite, normalized log probabilities before conversion to a float64 probability map. Model failures propagate with no fallback.

New runs save a canonical PNG, probability.npy and a completion report with source/model identity, prior, preprocessing, dimensions and timing. Existing directories are rejected. Pretrained files were downloaded fresh into Veyo/model-cache through upstream loaders. No old experiment code, environments, pins or weights were carried over.

Verification:
- All 20 unittest checks pass (11 loader, 9 inference). Mathematical contract tests use explicit fixtures/test doubles; the following run uses the genuine pretrained model.
- Actual product JPEG: 683 x 1024, probability array (1024, 683), all values finite and nonnegative, sum 1.0.
- First load, including downloads: 52.72 seconds; one CPU inference: 1.44 seconds using four threads. This is a single-image observation, not a throughput benchmark.
- Reloaded saved artifacts independently; checked source and probability-file hashes, shape, normalization and canonical-image mode/size.
- Repeated the CLI against the same output directory: it returned a clear error without changing any artifacts.
- Confirmed model-cache and outputs stay ignored by Git.

Choice and tradeoff: retain the original canonical resolution for direct coordinate alignment and use a recorded uniform spatial prior. Larger images may take more memory and time; center-prior sensitivity and model accuracy on ads remain unvalidated. The cache setting is process-wide; concurrency and durable job execution are future work.

Local result: outputs/ordinary-baseline (ignored). No product score or heatmap has been generated yet. Next, mark the four-product target from the canonical image and implement probability-based scoring and an aligned overlay.

User owns staging/commits/pushes. Suggested commit: `feat: add real DeepGaze inference`.

## 2026-09-30 — Rectangle scoring checkpoint

Added `veyo.scoring.score_region` and six focused tests. It validates the map and rectangle, then sums probability within the selected region, correcting only small numerical normalization drift. The user approved (55, 440, 645, 960) for all four products before scoring.

Verification: all 26 tests pass from backend with `.venv/bin/python -B -m unittest discover -s tests -v`. An initial invocation from the repository root failed package imports; rerunning from the documented backend working directory resolved that invocation error. Verified the stored probability-file hash against its inference report and checked canonical dimensions before scoring the existing genuine result. Score: 0.38006978025813865 (38.01%); box area: 43.87% of the image. No model rerun or modification of saved inference artifacts.

Limits: the box includes background; this value is not an ad performance or CTR measurement. The function assumes callers supply the matching canonical probability map. Persistent target identity and score records remain unimplemented.

Collaboration preference reaffirmed: one small implementation, explain what it does, stop for review, and present meaningful architecture alternatives for the user to choose before implementing them. User owns Git mutations. Suggested checkpoint commit: `feat: add validated rectangle attention scoring`.

Next review: understand [top:bottom, left:right], then choose whether the next small increment records a reproducible target/score file or displays the aligned heatmap. Do not implement either before that checkpoint.
