# Model experiment environment

This setup supports the first DeepGaze IIE experiment. It does not implement inference, a web API, or a frontend.

## Files and responsibilities

- `backend/.venv/`: isolated Python interpreter links and installed packages; ignored by Git.
- `backend/requirements.in`: direct dependencies and exact source commits chosen for this experiment.
- `backend/requirements.txt`: full installed-version snapshot, generated from the new environment. Commit this file with the direct dependency list.

NumPy represents images and probability grids. Pillow decodes images. PyTorch executes the model; torchvision supplies backbone components. DeepGaze supplies the pretrained saliency architecture. CLIP, einops and other supporting packages are required by imports in the current upstream package, even though this experiment uses IIE.

## Reproduce on a machine with Python 3.12

From the Veyo repository root:

```sh
python3.12 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
backend/.venv/bin/python -m pip check
```

The initial local environment uses the available bundled Python 3.12.14 interpreter. Its virtual environment depends on that base installation remaining available. For a standalone setup, install Python 3.12 independently and recreate the environment with the commands above. No packages or model caches were copied from the previous experiment.

To work in the environment from VS Code's terminal:

```sh
source backend/.venv/bin/activate
python --version
python -m pip check
```

Activation changes which Python the shell resolves; it does not start Veyo or install anything. VS Code can use `backend/.venv/bin/python` as its interpreter.

## Verification boundary

Check package consistency, import DeepGazeIIE, and decode the supplied JPEG. Importing the class does not load pretrained weights or produce a prediction. Full model loading and inference are the next increment.

The version snapshot is evidence for this macOS ARM/Python 3.12 installation, not a guarantee for Linux or CUDA. Validate the deployment environment separately. There is no hash-locked wheel manifest yet. Keep the snapshot untouched unless deliberately updating dependencies; reinstall from it rather than resolving requirements.in for reproduction.

## First experiment input

Use `data/samples/the-ordinary-review-is-this.jpeg`. The user selected the four products together as the target, before any predictions were generated. Exact annotation boundaries remain to be defined. A rectangle containing the group will include intervening background; an object mask would be more precise but require more annotation work.
