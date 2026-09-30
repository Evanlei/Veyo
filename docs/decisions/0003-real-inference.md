# 0003 — Real CPU inference on the canonical image grid

Date: 2026-09-30
Status: Implemented and verified on the supplied JPEG; details in the build log.

Use pretrained DeepGaze IIE in evaluation mode under PyTorch inference_mode. One predictor loads the model once and can serve sequential calls; model errors propagate. There is no fallback model or fabricated heatmap. CPU is the baseline before considering hosting hardware.

The canonical RGB image is converted from H x W x 3 to a float32 tensor with shape 1 x 3 x H x W. Pixel values remain in 0..255, as expected by the upstream model; its backbone handles normalization internally. No external resizing is done, so the returned H x W probability grid maps directly to the canonical image.

Use a normalized uniform log-density as the center-bias input and record this setting. It avoids adding a spatially varying center prior, but does not remove center biases learned by the model or establish calibration on ads. Compare against other priors later as a separate experiment.

Require output shape 1 x 1 x H x W, finite log probabilities, and a log total within 1e-4 of zero. Convert to float64 probabilities and correct only rounding drift. Never rescue materially unnormalized predictions by silently treating them as valid.

The local CLI saves the canonical image, probability.npy and report.json in a new output directory. The report is written last to mark successful saving, and records the input hash, model source commit, preprocessing, prior, dimensions and timings. Existing runs cannot be overwritten. A disk error can leave partial output without a completion report; this is not a durable job system yet.

Pretrained backbone and model files are downloaded through upstream loaders into model-cache, not copied from earlier experiments. Torch's cache setting is process-wide. The intended future worker owns its process and predictor; concurrent inference on this instance has not been validated.

The CLI does not draw heatmaps or compute target scores. The user has already selected the four products semantically; annotate their boundaries from the original image before inspecting the probability visualization. Synthetic probability arrays exist only inside explicitly labeled unit tests for mathematical and error contracts; they are never returned as application predictions.
