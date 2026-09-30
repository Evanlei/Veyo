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
