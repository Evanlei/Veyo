# 0002 — Canonical RGB images before annotation and inference

Date: 2026-09-30
Status: Implemented

`load_image(path)` accepts a filesystem string or Path and returns a fully decoded, independent Pillow RGB image. It validates the decoded format as PNG or JPEG, rejects animated PNGs, applies EXIF orientation, composites transparency onto opaque white, and preserves the resulting dimensions. It never changes the source file.

The user chose white as the transparency background. Predictions will describe the creative displayed on white; a different background may change visual attention. RGBA compositing handles partial transparency and palette transparency, whereas simply dropping alpha could expose hidden colors. Using a single path also requires temporary image buffers, so we should benchmark memory before accepting large uploads.

Orientation is applied before target annotation. The canonical image's dimensions and pixels must be shared by the future browser, target mask, and model. A 90-degree EXIF rotation swaps width and height; this is not a resize. No inference-specific resizing is introduced in this feature.

Validation uses file contents, not filename extensions. Missing-file and decoding errors propagate to the caller; unsupported formats and animation raise ValueError. No replacement image is returned. Upload byte limits, explicit decoded-pixel limits and color-profile management remain future ingestion work before exposing uploads through an API. Pillow's built-in decompression-bomb protections remain enabled.

Eleven unittest checks cover image independence, unchanged originals, pixel preservation, RGB/grayscale/palette inputs, full and partial transparency, rotation/mirroring, format spoofing, animation, corrupt/truncated data, and missing files. Tiny generated pixel fixtures test the loader contract; they are not substitute ads or model outputs. No dependency was added for tests.
