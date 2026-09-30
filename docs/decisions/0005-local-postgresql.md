# 0005 — Local PostgreSQL with Docker Compose

The user chose PostgreSQL now rather than interim JSON analysis records, and Docker rather than a native database installation. This increment only provisions the local database; schema design and migrations remain separate checkpoints.

Use a single official PostgreSQL 18 Bookworm service, a localhost port, an ignored randomly generated local password, a named data volume and a readiness check. The volume mount follows PostgreSQL 18's versioned data layout. No application container, cloud resources or new Python dependencies are introduced.

Tradeoffs: Docker makes the database setup portable but requires the engine running and consumes resources. A major-version tag allows minor updates but does not exactly pin image bytes. Named volumes survive container replacement but need separate backups. The local bootstrap account has superuser privileges; least-privilege application accounts are a later integration requirement.

Agreed future behavior: changing a rectangle creates a new score record rather than overwriting history. Proposed tables are images, analysis_runs and region_scores; they are not implemented here.

References: https://hub.docker.com/_/postgres and https://docs.docker.com/reference/compose-file/services/.
