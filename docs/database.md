# Local PostgreSQL

Open Docker Desktop. Run commands from the Veyo repository root.

## Configuration

`compose.yaml` describes one service, `db`, using the official PostgreSQL 18 Bookworm image. The major version and OS variant are explicit; the tag can receive minor updates and is not a byte-for-byte image pin. Review upgrades deliberately.

For a fresh checkout, copy `.env.example` to `.env` and replace the placeholder password before first startup. The initial setup generated a random local password in the ignored `.env`; do not commit it. The environment variable initializes the password only on an empty data volume. Editing it later does not rotate the database password.

```sh
docker compose up -d --wait
docker compose ps
docker compose exec db psql -U veyo -d veyo -c 'SELECT current_database(), version();'
```

- `ports` exposes PostgreSQL at `127.0.0.1:5432` on this Mac. A future host-run API connects there; a future Compose service would use `db:5432`.
- `postgres_data` is a Docker-managed named volume mounted at `/var/lib/postgresql`, following the PostgreSQL 18 image layout. It holds the database files independently of the container.
- The health check uses `pg_isready` to check server readiness, not schema correctness or application credentials.
- There is no restart policy yet: start the database explicitly when developing.
- The bootstrap `veyo` user is a local development superuser. A deployed application needs separate restricted credentials; do not reuse this setup as production configuration.

## Stop and resume

```sh
docker compose stop
docker compose start --wait
```

`docker compose down` removes the container and network but retains the named volume; `docker compose up -d --wait` reuses it. **Adding `--volumes` to down deletes the database volume.** A volume is persistent storage, not a backup.

The database currently has no Veyo application tables, migrations, or Python connection integration. Those are separate increments.
