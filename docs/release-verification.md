# Release verification — 2026-10-24

## Completed checks

| Boundary | Evidence |
| --- | --- |
| Frontend production build | Strict TypeScript and Vite production build pass. |
| Frontend math/presentation checks | Six tests pass across target geometry and metric formatting. |
| Backend contracts and HTTP integration | 50 tests pass, including error propagation, isolation, uploads, history, cache reuse, comparisons, exports, production deep links, asset caching, and API/static route boundaries. |
| Shipped npm runtime dependencies | `npm audit --omit=dev` reports zero known vulnerabilities. |
| Desktop interface | Safari renders the library, Figma-based workspace, real heatmap, adjustment dialog, revision workflow, and comparison screen. |
| Responsive behavior | Comparison controls and image panels stack at a narrower effective viewport using Safari page zoom; zoom restored afterward. This is not a physical mobile-device test. |
| Real model | Genuine DeepGaze IIE model commit `c7db17e2d1d7ea6468ffdee2cfaddf141095dcff`. No test predictor is used in the live smoke test. |
| Deployment container | Linux/amd64 image builds successfully with the pinned CPU environment and pretrained weights. It starts as the nonroot `veyo` user. |

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

## Publication status

Veyo is not published to a public URL. The owner explicitly selected **keep
cloud spending disabled**. No cloud builds, Cloud Run services, or paid storage
resources were created. The existing Google Cloud project remains intact;
Firebase Hosting configuration and its npm CLI dependency have been removed.

The optional Cloud Run script's shell syntax passes. Without paid opt-in it
exits with status 2 before invoking a cloud command; that guard was exercised.
The GCS adapter and remote hosting path still require cloud verification if the
owner later changes the spending decision. See [deployment](deployment.md).
Never treat local verification as proof of public deployment.
