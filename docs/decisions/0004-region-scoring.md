# 0004 — Rectangle probability scoring

Use a standalone NumPy function, `score_region(probability, box)`, returning a fraction in [0, 1]. It takes an H x W normalized probability map and integer canonical-image coordinates (left, top, right, bottom), with right and bottom excluded. Array slices are [top:bottom, left:right].

Reject empty/nonreal/nonfinite/negative or unnormalized maps and invalid/out-of-bounds boxes. Normalize only accepted numerical drift (absolute total tolerance 1e-6); never silently repair a materially invalid map. Inputs remain unchanged.

Keeping the calculation independent of inference and file storage allows exact mathematical tests and later reuse by the API and worker. Rectangles are simple to mark and audit, but include background; segmentation and polygons remain future choices. Larger boxes can capture more probability without improving creative quality. Scores represent predicted spatial fixation mass, not measured human attention, CTR or sales.

The user approved the four-product rectangle (55, 440, 645, 960) on the 683 x 1024 canonical Ordinary image before reviewing its score. The selected geometry covers 590 x 520 pixels. The function cannot itself verify image identity or target correspondence; the future saved-target integration must bind geometry to the canonical image and inference run.

No storage schema, API or heatmap implementation was added. These are separate review checkpoints.
