# 0007 — One container, cloud spending disabled

Date: 2026-10-24. Updates decision 0006's hosting arrangement.

The user chose to keep cloud spending disabled and approved simplifying hosting
to one Docker application. The original request for a “web.app” meant a web
application; Firebase's domain is not a product requirement.

Build React in a Node 24 stage, then copy its compiled files into the Python
runtime image alongside the API and pretrained model weights. FastAPI serves
static assets and known client-side routes after the API routes. Unknown API
endpoints and missing assets retain genuine 404 responses. Private API data is
never cached; hashed build assets can be cached, and HTML revalidates.

Compose exposes the complete app at localhost:8000 with a persistent named
volume. Local development can still use Vite's hot reload proxy. There is no
PostgreSQL service, Firebase Hosting configuration, or Firebase CLI dependency.
The existing cloud project is left intact; no account billing settings change.

Retain the optional GCS adapter and Cloud Run deployment script for future use,
but require explicit paid-deployment opt-in before any cloud command executes.
The present decision does not authorize that opt-in. A future container host
must supply persistent storage or an explicitly configured object-store adapter.

This simplifies release coordination and keeps all browser requests on one origin.
It does not create a free public Python host. Public deployment remains pending
a hosting decision compatible with the owner's spending preference.
