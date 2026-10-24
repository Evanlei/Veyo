# Storage

Veyo no longer requires PostgreSQL. See [decision 0006](decisions/0006-file-backed-studio.md).

Local development stores JSON records and separate images under the ignored
`storage/` directory. `VEYO_STORAGE_DIR` can select another directory. The default
is resolved from the repository root, independent of the launch directory.

Docker Compose starts the complete interface, API, and model in one container,
using a named `creative_files` volume. Optional paid Cloud Run hosting uses a
private Google Cloud Storage bucket through `VEYO_GCS_BUCKET`; container-local
files are not relied on for durable user data in that configuration.

Use the app's complete-project ZIP export for portable creative and evidence
backups. Back up the private workspace key from Settings separately; it controls
access and is deliberately absent from project exports. Cloud backups and object
retention policies should be configured according to the deployment's needs.

The historical PostgreSQL setup is recorded in decision 0005 and the build log.
No command has been run to delete its existing Docker volume. Avoid deleting
volumes unless you have deliberately backed up and retired their contents.
