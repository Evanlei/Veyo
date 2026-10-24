# 0008 — Free public recorded demo

Date: 2026-10-24. Updates the public hosting portion of decision 0007.

The owner selected Pixel's approach: publish a static replay of genuine backend
runs while keeping fresh uploads and model inference local. Cloud spending must
remain disabled. Firebase Hosting serves the demo at
https://veyo-attention-studio.web.app with no linked billing account.

Build the existing React interface in a separate `demo` mode and output directory.
A read-only adapter serves three original/revision pairs from a versioned public
manifest. It blocks mutations before fetch and never creates or transmits a
workspace key. Persistent labels identify recorded results; actions say “View
recorded revision” or “Show saved analysis” rather than implying new computation.

Capture only the repository's fictional ads in an isolated temporary workspace.
Use the production analysis service, preserve genuine model identity and image
hashes, and publish saved heatmaps, overlays, reports, and project archives.
Compare completed compatible runs using their saved metrics. Retain losing
revisions as well as gains. Stable public IDs preserve deep links.

Validate artifact hashes, image geometry, references, and model identity before
building. Test mutation rejection and comparisons, then verify the published
artifacts, routes, downloads, and browser interface independently. No fake model
or fabricated heatmaps are part of this mode.

Deploy only static Hosting files. The deploy script checks that billing is
explicitly disabled and rejects server rewrites. It never enables billing or
provisions compute. The optional paid Cloud Run script remains guarded. The
complete local application and its private file repository are unchanged.

This makes the review workflow publicly explorable at no cloud spend. It does
not let visitors analyze their own creatives online. That feature would require
a separate compute and persistence decision.
