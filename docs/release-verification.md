# Release verification — 2026-10-24

## Completed checks

| Boundary | Evidence |
| --- | --- |
| Frontend production build | Strict TypeScript and Vite production build pass. |
| Frontend math/presentation checks | Six tests pass across target geometry and metric formatting. |
| Backend contracts and HTTP integration | 47 tests pass, including error propagation, isolation, uploads, history, cache reuse, comparisons, and exports. |
| Shipped npm runtime dependencies | `npm audit --omit=dev` reports zero known vulnerabilities. |
| Desktop interface | Safari renders the library, Figma-based workspace, real heatmap, adjustment dialog, revision workflow, and comparison screen. |
| Responsive behavior | Comparison controls and image panels stack at a narrower effective viewport using Safari page zoom; zoom restored afterward. This is not a physical mobile-device test. |
| Real model | Genuine DeepGaze IIE model commit `c7db17e2d1d7ea6468ffdee2cfaddf141095dcff`. No test predictor is used in the live smoke test. |

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

## Deployment status and remaining verification

The Firebase Hosting, Cloud Build, private GCS storage, service-account roles,
and Cloud Run deployment source are prepared. The Google Cloud SDK is available
locally through `npm run cloud -- ...`; the Firebase CLI is installed through npm.
Deployment shell syntax has been checked.

Both Firebase and Google Cloud CLIs are now authenticated. The requested Google
Cloud project `veyo-attention-studio` exists and is owned by the signed-in user.
Adding Firebase resources returned 403; the Firebase console confirms first-time
terms acceptance is still required. The existing project is selected in that
setup form. No billing accounts are available and project billing is disabled.
No live `web.app` URL has been published yet.

After the user completes Firebase terms and billing setup, run
`bash scripts/deploy.sh veyo-attention-studio`, then run the smoke test against
the deployed URL. See [deployment](deployment.md). The container and remote GCS
adapter still require cloud verification. CI configuration is committed but has
not been run on GitHub; commits remain local to the branch. Never treat the local
smoke result or the successful frontend build as proof of cloud publication.
