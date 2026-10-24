# Release verification — 2026-10-24

## Completed checks

| Boundary                               | Evidence                                                                                                                                                                           |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Frontend production build              | Strict TypeScript and Vite production builds pass for both full and demo modes.                                                                                                    |
| Frontend math/presentation checks      | Nine tests pass across target geometry, metric formatting, and recorded-demo contracts.                                                                                            |
| Backend contracts and HTTP integration | 50 tests pass, including error propagation, isolation, uploads, history, cache reuse, comparisons, exports, production deep links, asset caching, and API/static route boundaries. |
| Shipped npm runtime dependencies       | `npm audit --omit=dev` reports zero known vulnerabilities.                                                                                                                         |
| Desktop interface                      | Safari renders the library, Figma-based workspace, real heatmap, adjustment dialog, revision workflow, and comparison screen.                                                      |
| Responsive behavior                    | Comparison controls and image panels stack at a narrower effective viewport using Safari page zoom; zoom restored afterward. This is not a physical mobile-device test.            |
| Real model                             | Genuine DeepGaze IIE model commit `c7db17e2d1d7ea6468ffdee2cfaddf141095dcff`. No test predictor is used in the live smoke test.                                                    |
| Deployment container                   | Linux/amd64 image builds successfully with the pinned CPU environment and pretrained weights. It starts as the nonroot `veyo` user.                                                |

## Complete live smoke flow

Executed through `http://127.0.0.1:5173/api/`, including Vite's API proxy:

1. Create a sample project with known target geometry.
2. Run real CPU inference and save the baseline.
3. Create a localized brightness adjustment as a new creative revision.
4. Confirm corresponding target annotations and analyze the revision.
5. Compare the three corresponding elements.
6. Verify exported overlays preserve the canonical 900 × 1125 image grid.
7. Upload a separate revision using multipart image intake.
8. Export a ZIP containing three creatives and two analysis overlays.
9. Confirm another workspace key receives 404 for the original image.

The smoke report was saved locally in ignored `outputs/release-smoke.json`.
Baseline combined attention share: **0.6707125959**. Revision share:
**0.6780756959**. Target changes: Products **+0.4242 pp**, Headline **+0.4883 pp**,
Brand **−0.1761 pp**. Baseline analysis took 6.126 seconds and revision analysis
2.405 seconds in this observation. These timings are not throughput benchmarks.

A separate browser-created whole-creative brightness revision was also analyzed
and compared. The interface displayed both positive product attention change and
negative brand attention change. No higher-score result is presented as proof of
better advertising performance.

## Linux container verification

The same nine real-model smoke checks also pass against the actual Linux/amd64
deployment container at local port 18080. Its report is saved in ignored
`outputs/container-smoke.json`. Combined attention shares were 0.6707125865 and
0.6780757550, matching the macOS results to normal floating-point tolerance.
Baseline and revision analyses took 17.404 and 8.784 seconds on the local
cross-architecture Docker run, not native Google Cloud hardware. The temporary
verification container was stopped after testing. This incurred no cloud compute.

## Unified application verification

After the owner chose to keep cloud spending disabled, the image was updated to
build and serve React alongside FastAPI and the model. The Linux/amd64 image
`veyo:unified` builds successfully with Node 24 in its frontend build stage and
starts as nonroot user `veyo`. No Node or Firebase CLI is needed in the runtime.

The complete nine-check real-model flow passes at port 18080, saved locally in
ignored `outputs/unified-container-smoke.json`. Combined attention shares are
0.6707125865 and 0.6780757550. Observed baseline/revision times were 20.304 and
8.703 seconds under local CPU emulation; these are not cloud benchmarks.

Actual HTTP checks confirm the HTML shell, direct guide/settings/creative/compare
routes, cacheable hashed JavaScript, JSON API failures, missing assets, and
traversal rejection. A sample project was created on a named volume, its
container removed and replaced, and its saved metadata, targets, and PNG
successfully fetched using the same workspace key. The temporary credential
file was removed after that check.

Safari renders the compiled interface from the same container port, and `/guide`
still renders after a direct reload. A browser-created Forma project completed
real inference and displayed the heatmap, 67.1% combined target share, individual
metrics, and saved history. This verifies the production origin and SPA routing
rather than only Vite's development proxy. Compose configuration
validation passes. Native Linux/arm64 has not been separately built or tested.

## Public recorded demo verification

Published to **https://veyo-attention-studio.web.app** on 2026-10-24.
Firebase Hosting version `282be40bd887ec5e` finalized successfully. Project
billing was checked after publication: `billingEnabled: false`, with no linked
billing account. No cloud builds, Cloud Run services, or paid storage resources
were created.

The recorder exercised the production service on three original/revision pairs.
All six completed runs retain the actual model identity and evidence. Fieldwork's
revision has lower combined target attention, and that loss remains visible.
The build validates 27 artifact hashes and the recording's IDs and geometry.

The live HTTPS checker passes for every artifact, all 18 canonical PNG dimensions,
three ZIP contents, creative/comparison deep links, guide/demo details routes,
security/cache headers, and unknown API or missing-asset 404 responses. Its local
report is `outputs/public-demo-verification.json`. This verifies saved results,
not public live inference. The full backend remains local.

Chrome also renders the compiled demo's library, Forma saved heatmap, recorded
revision, and comparison locally. The public HTTPS interface also renders the library, saved heatmap, and comparison
with both positive and negative target changes. A Chrome screenshot confirms
that the deployed images, overlays, and persistent recorded-demo banner load.

The optional Cloud Run script remains disabled without explicit paid opt-in.
The GCS adapter and remote full-app hosting path still require cloud verification
if the owner changes the spending decision. See [deployment](deployment.md).
