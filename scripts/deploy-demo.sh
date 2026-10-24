#!/usr/bin/env bash
# Publish only the static recorded demo. Never enable billing or deploy compute.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
PROJECT_ID="$(node -e 'process.stdout.write(JSON.parse(require("node:fs").readFileSync(".firebaserc", "utf8")).projects.default)')"
billing_enabled="$(bash scripts/google-cloud.sh billing projects describe "$PROJECT_ID" --format='value(billingEnabled)')"
if [[ "$billing_enabled" != "False" ]]; then
  echo 'Static demo deployment stopped: verify that project billing is disabled before continuing.' >&2
  exit 2
fi
node -e "const c=require('./firebase.json').hosting; if(c.public!=='frontend/demo-dist'||c.rewrites.some(r=>r.run||r.function||r.destination!=='/index.html')) throw Error('Only the static demo may be deployed');"
npm run build:demo
npx --yes firebase-tools@15.34.1 deploy --only hosting --project "$PROJECT_ID" --non-interactive
