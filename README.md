# metabase-toolchain

A set of command-line tools for Metabase: importing and exporting dashboards, collections, permissions, and database configuration; and managing the MongoDB schema-stub snapshot used during import.

The main CLI is `import_metabase`, which loads a previously exported `export.json` into a target Metabase instance. It combines direct MongoDB writes (to seed the target schema) with Metabase HTTP API calls (to create users, collections, dashboards, cards, and settings). Companion CLIs are `export_metabase` and `manage_snapshot_db`.

**Compatible Metabase version:** `0.44.6` (Docker image tag: `metabase/metabase:v0.44.6`).

## Prerequisites

- Docker and `docker compose` (for the local stack; cloud deployments use their own infrastructure).
- Python 3.9+ with `pip` — a virtualenv is recommended.
- `make`.
- A reachable target Metabase instance and a reachable MongoDB / AWS DocumentDB.

## Local development setup

The steps below reproduce the full import flow using a local Metabase + MongoDB stack from `src/infra/docker-compose.yml`, with `test/test_data/export.json` as the sample input.

> For **cloud / production** deployments, follow the separate TED-SWS installation manual. This section covers local development only.

### 1. Create `src/.env`

```bash
cp src/.env.example src/.env
```

The committed template has local-dev defaults (Metabase on `3001`, Mongo on `27018`, admin `a@a.com` / `okokok123`, data source name `TEDSWS MongoDB`, database `aggregates_db`). Edit any value you want to change.

### 2. Start the compose stack

```bash
make up
```

Starts `metabase`, `metabase-postgres`, and `mongo` on a shared `metabase-net` bridge network. Verify they are healthy:

```bash
docker compose -f src/infra/docker-compose.yml -p metabase-toolchain ps
```

### 3. Complete Metabase's first-run wizard

Open `http://localhost:3001` and step through setup. Set the admin email and password to match `METABASE_USER` / `METABASE_PASSWORD` in `src/.env` (defaults: `a@a.com` / `okokok123`). If Metabase's password policy rejects the default, pick a stronger one and update `src/.env` to match.

Skip the "Add your data" step — the data source is registered manually in the next step.

### 4. Register the `TEDSWS MongoDB` data source

In **Admin settings → Databases → Add database**:

| Field | Value |
|---|---|
| Database type | MongoDB |
| Display name | `TEDSWS MongoDB` (exact — spaces matter) |
| Host | `mongo` |
| Port | `27017` (internal container port) |
| Database name | `aggregates_db` |
| Username / Password | (empty) |
| Authentication database | (empty) |

Alternatively, toggle on "Use a connection URI" and paste `mongodb://mongo:27017/aggregates_db`.

Save. Metabase runs an initial sync.

### 5. Install the CLI

```bash
make install-cli
```

### 6. Run the import

```bash
import_metabase test/test_data/export.json
```

On success, the Metabase UI shows the imported users, collections, dashboards, and cards. Re-running is safe — existing resources are updated rather than duplicated.

### Useful targets

- `make test` — run the test suite. Needs `mongo` running; no pre-population required.
- `make init-mongo` — **optional.** Drops and re-creates the local Mongo database named by `DB_NAME` with a placeholder document. Useful for regenerating the bundled snapshot (`manage_snapshot_db -u`) from a known state, or for giving the e2e tests non-empty collections to exercise.
- `make down` — stop containers (preserves volumes).
- `make rebuild` — wipe volumes, pull fresh images, and start.

## Commands

| Command | Purpose |
|---|---|
| `import_metabase <export.json>` | Import an exported Metabase configuration into a running Metabase instance. |
| `export_metabase <host> <user> <password> [file]` | Export the current Metabase configuration to a JSON file. Defaults to `./data/export.json`. |
| `manage_snapshot_db` | Manage the bundled MongoDB schema-stub snapshot (create, inject, remove). See `--help`. |

## Environment variables

All variables live in a **single `src/.env` file**. It is consumed by:

- The Python CLIs via `dotenv`.
- `docker-compose` (`make up`, `make rebuild`) via `--env-file .env` passed from the Makefile.

Start from the committed template:

```bash
cp src/.env.example src/.env
```

### Application variables

Read by the Python CLIs.

| Variable | Required for | Default | Purpose |
|---|---|---|---|
| `METABASE_HOST` | `import_metabase`, `export_metabase` | — | Base URL of the target Metabase instance. If the scheme is omitted, `https://` is prepended automatically. |
| `METABASE_USER` | `import_metabase`, `export_metabase` | — | Email of the Metabase admin used to authenticate. |
| `METABASE_PASSWORD` | `import_metabase`, `export_metabase` | — | Password for that admin user. |
| `DB_AUTH_URL` | `import_metabase`, `manage_snapshot_db` | — | MongoDB / AWS DocumentDB connection string. The importer connects to it directly to inject a schema stub before calling the Metabase API. |
| `DB_NAME` | `import_metabase`, `manage_snapshot_db` | — | Name of the MongoDB database the snapshot is injected into. Must match the database name registered as the Metabase data source. |
| `MONGO_DB_USER` | — | unset | Optional override. When set, rewrites `details.user` of any Metabase-registered Mongo data source during import. Use when the target environment's Mongo credentials differ from those baked into `export.json`. |
| `MONGO_DB_PASS` | — | unset | Optional override for the registered Mongo source password. |
| `MONGO_DB_HOST` | — | unset | Optional override for the registered Mongo source host. |
| `MONGO_DB_PORT` | — | unset | Optional override for the registered Mongo source port (cast to `int`). |
| `METABASE_DB_NAME` | — | `TEDSWS MongoDB` | Name of the Metabase-registered data source the importer looks up when mapping tables and fields from `export.json`. Override if your target Metabase uses a different display name. |
| `METABASE_API_SSL_VERIFY` | — | `false` | Set to `1` or `true` to enable TLS certificate verification on Metabase API calls. Defaults to disabled. |

### Infra variables

Consumed by `src/infra/docker-compose.yml` for `${VAR:-default}` substitution.

| Variable | Compose default | Example | Purpose |
|---|---|---|---|
| `METABASE_VERSION` | `v0.44.6` | `v0.44.6` | Metabase Docker image tag. Toolchain is tested against `0.44.6`. |
| `METABASE_HOST_PORT` | `3000` | `3001` | Host-side port the Metabase container is published on. |
| `MB_SITE_URL` | `http://localhost:3000` | `http://localhost:3001` | Public URL Metabase advertises for itself. |
| `JAVA_TIMEZONE` | `UTC` | `UTC` | JVM timezone for the Metabase container. |
| `MB_DB_DBNAME` | `metabaseappdb` | `metabaseappdb` | Postgres database storing Metabase's **internal state** (dashboards, users, sessions). Not a data source. |
| `MB_DB_USER` | `metabase` | `metabase` | Postgres user for the Metabase app DB. |
| `MB_DB_PASSWORD` | `metabase` | `metabase` | Postgres password for the Metabase app DB. |
| `MB_DB_HOST_PORT` | `5432` | `5432` | Host-side port for the Postgres container. |
| `MONGO_VERSION` | `6` | `6` | MongoDB Docker image tag. Used as the schema-stub target for `import_metabase`. |
| `MONGO_HOST_PORT` | `27017` | `27018` | Host-side port for the MongoDB container (bound to 127.0.0.1). |

## Security

Automated scanning runs on every push and pull request via GitHub Actions:

- **CodeQL** (`.github/workflows/codeql.yml`) — semantic SAST for Python source. Findings appear under the repo's **Security → Code scanning** tab and as inline PR annotations.

For quick local checks before opening a PR:

```bash
pip install pip-audit bandit
pip-audit                                         # Python dependency CVEs
bandit -r src/metabase/                           # Python source SAST
docker run --rm aquasec/trivy:latest image \
    metabase/metabase:v0.44.6                     # base image CVEs
```

## License

Apache 2.0 — see [LICENSE](LICENSE).
