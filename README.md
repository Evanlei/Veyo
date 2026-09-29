# Veyo

Attention analysis and creative review for marketing teams.

Veyo is being built to help teams inspect what draws predicted visual attention in a static ad, compare revisions, and keep a reproducible record of creative experiments. It supports PNG/JPEG social ads, banners, product promotions, and other static creatives.

## Status

Initial repository setup. The application and its model integration have not been implemented in this repository yet. The capabilities and stack below describe the planned product.

## First milestone

Start with a real DeepGaze IIE experiment using sample ads, then build one complete workflow:

1. Upload a static ad.
2. Manually mark a target, such as a product, logo, headline, or call to action.
3. Run DeepGaze IIE to predict a spatial fixation distribution.
4. Display an aligned heatmap and the predicted attention share inside the target.

Show the target's share of image area alongside its attention share to make the result easier to interpret. Model failures must be visible errors, never substitute heatmaps.

The next milestone is comparing an uploaded revision with its own correctly marked corresponding target. Later work adds campaign priorities, saved experiment history, and controlled creative adjustments.

## Planned architecture

One repository, with a React interface, a Python API, and a separate Python process for inference. The API and worker share the analysis code. The worker keeps slow model execution separate from web request handling.

| Component | Technology | Purpose |
| --- | --- | --- |
| Frontend | React, TypeScript | Uploads, target selection, heatmaps, and comparisons |
| API | Python, FastAPI | Validation, asset management, and analysis jobs |
| Inference | PyTorch, DeepGaze IIE | Predicted fixation distributions |
| Image processing | Pillow; OpenCV as needed | Image preparation and coordinate handling |
| Database | PostgreSQL | Projects, assets, jobs, variants, settings, and scores |
| File storage | Local files initially | Uploaded creatives and generated results |

Introduce Docker and focused automated checks as components are implemented. Consider S3 for shared file storage and SQS for job delivery when deployment requires them. Benchmark inference before choosing GPU hosting.

## Interpretation and limits

- Scores describe model-predicted fixation probabilities. They do not establish click-through rates, sales, or measured human attention.
- DeepGaze IIE provides spatial predictions, not a temporal gaze path.
- Each revision needs a verified target annotation; moving an element can invalidate its previous coordinates.
- Flattened images support analysis and controlled adjustments. Precise layout changes require separate assets or a structured design.
- A higher model score alone does not prove that an ad is better. Optimization will need evaluation beyond the scoring model.

## Development

Build and verify one complete increment at a time. Record significant design decisions and their tradeoffs as the project develops. Reproducible setup instructions will accompany the first runnable component.

Keep local ads, generated results, model weights, secrets, and installed dependencies out of Git. Small, deliberately selected test fixtures can be tracked separately when appropriate.

## Attribution

The workflow is inspired by [Pixel](https://github.com/EnesYilmazcode/Pixel). The planned prediction model is [DeepGaze IIE](https://github.com/matthias-k/DeepGaze), by Linardos, Kümmerer, Press, and Bethge.

Veyo's application and evaluation work will build on that research; it does not claim to have developed or trained DeepGaze.
