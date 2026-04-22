# Upgrade Notes

Summary of changes made to modernise `metabase-toolchain`: packaging migration, dependency upgrades, local Metabase stack, and Claude Code configuration.

---

## 1. Packaging: `setup.py` → `pyproject.toml`

Replaced the legacy setuptools layout with a PEP 621 `pyproject.toml` using the `poetry-core` build backend.

**Removed:**
- `setup.py`
- `requirements.txt`
- `requirements.dev.txt`

**Added:**
- `pyproject.toml` — single source of truth for metadata, runtime deps, optional extras, console scripts, and build config.

### Console scripts (unchanged, still registered)
| CLI | Entry point |
|---|---|
| `export_metabase` | `metabase.migration.entrypoints.cli.cmd_export_metabase:main` |
| `import_metabase` | `metabase.migration.entrypoints.cli.cmd_import_metabase:main` |
| `manage_snapshot_db` | `metabase.migration.entrypoints.cli.cmd_manage_db_snapshot:main` |

### Python version floor raised
- Was: `>=3.7`
- Now: `>=3.9,<3.15` — widest useful range; dependency floors adjusted to stay compatible.

---

## 2. Dependency upgrades (for security-scan compatibility)

All runtime deps bumped to the latest available release within a safe major range.

| Package | Before | After | Notes |
|---|---|---|---|
| pydantic | `~=1.9.1` | `>=2.6,<3.0.0` | **Major jump (v1 → v2)**. One `BaseModel` in the codebase (`MigrationData`) — verified imports and instantiates under v2. Floor relaxed for Python 3.9 compatibility. |
| urllib3 | `==1.23` | `>=2.0,<3.0.0` | **Major jump (v1 → v2)**. Only use is `disable_warnings()`, still available in v2. |
| pymongo | `~=4.0.1` | `>=4.6,<5.0.0` | |
| requests | `~=2.28.1` | `>=2.31,<3.0.0` | |
| click | `~=8.1.0` | `>=8.1,<9.0.0` | |
| python-dotenv | `==0.21.1` | `>=1.0,<2.0.0` | |
| load-bar | `~=0.0.7` | `>=0.0.7,<1.0.0` | No newer release on PyPI. |

### Dev / optional extras (new `[project.optional-dependencies]`)
- **`test`** — `pytest>=8.0,<10`, `pytest-cov>=5.0,<8`, `coverage>=7.4,<8`
- **`lint`** — `ruff>=0.6.0`, `mypy>=1.11.0`
- **`dev`** — union of `test` + `lint`

`pytest` floor is `8` (not `9`) because pytest 9.0 requires Python 3.10+; 8.x preserves Python 3.9 support.

### Dropped
- `tox` + `tox-pytest-summary` — there was no `tox.ini`, so `make test-unit` never actually ran tox. `tox-pytest-summary` has been stuck at 0.1.2 since 2022. Replaced with direct `pytest`.

### Known leftover issue (out of scope, flagged)
`metabase/migration/model/migration_data.py` has two fields typed `Optional[Dict]` with `[]` as default. Pydantic v2's serializer emits a `UserWarning` at runtime — **not an error**. One-line fix when convenient:
```python
collections_graph: Optional[Dict] = None
settings: Optional[List[Dict]] = None
```

---

## 3. Makefile rewrite

Cleaned up and split into two clear sections: Python packaging, and the Metabase Docker stack.

### Python targets
| Target | What it does |
|---|---|
| `make install` | `pip install .` — runtime-only install |
| `make install-dev` | `pip install -e ".[dev]"` — editable + all dev tools |
| `make reinstall` | Uninstall + `--force-reinstall --no-cache-dir` |
| `make test` | `pytest tests` (was `tox -e unit`, which was broken) |

### Docker stack targets
| Target | What it does |
|---|---|
| `make up` | Start Metabase + Postgres (auto-bootstraps `infra/.env` on first run) |
| `make down` | Stop and remove containers (data preserved in named volumes) |
| `make rebuild` | `down -v` (wipes DB) + `pull` + `build --no-cache` + `up -d` |

---

## 4. Local Metabase stack

Added a minimal dev stack under `infra/`.

**Files:**
- `infra/docker-compose.yml` — `metabase/metabase:latest` + `postgres:15-alpine` as the Metabase application metadata DB.
- `infra/.env.example` — committed template; `infra/.env` is gitignored.

**Design choices:**
- Postgres bound to `127.0.0.1:5432` (not exposed on 0.0.0.0).
- Postgres healthcheck + `depends_on: service_healthy` on Metabase, so Metabase doesn't race the DB on cold start.
- Named volumes: `metabase-postgres-data` (DB), `metabase-plugins` (Metabase plugin cache).
- All tunables via `${VAR:-default}` — zero-config start, overridable via `infra/.env`.
- No Traefik / no build context — the reference TED-SWS compose style was used as a skeleton, but simplified since there's only one routable service.

**Usage:**
- `make up` → Metabase at `http://localhost:3000` (~1 minute first boot).
- `make rebuild` when the DB gets corrupted or you want a clean slate.

---

## 5. Claude Code configuration

Created `.claude/settings.local.json` (personal, gitignored) with:
- Broad permission allowlist — `Bash`, `Read`, `Edit`, `Write`, `Glob`, `Grep`, `mcp__gitnexus`.
- `defaultMode: "acceptEdits"` — auto-accept file edits without prompting.
- `enableAllProjectMcpServers: true` + `enabledMcpjsonServers: ["gitnexus"]` — auto-approves the gitnexus MCP server from `.mcp.json`.
- Empty `attribution.commit` / `attribution.pr` and `includeCoAuthoredBy: false` — strips the "Generated with Claude Code" trailer and `Co-Authored-By` lines from commits and PRs.

`.gitignore` updated to exclude `.claude/settings.local.json`.

> **Note:** MCP server changes only take effect at session start. A restart is required before gitnexus tools become available. Gitnexus also needs an indexed graph (`npx gitnexus analyze`) before any queries will return useful data.

---

## 6. Verification

All install paths tested in an isolated venv (`python3 -m venv`):

| Check | Result |
|---|---|
| `pip install .` | OK — all upgraded versions resolve and build |
| `pip install --force-reinstall --no-cache-dir .` | OK |
| `pip install -e ".[dev]"` | OK — ruff, mypy, pytest, pytest-cov, coverage installed |
| `pip check` | No broken requirements |
| `import metabase` + `MigrationData()` instantiation | OK on pydantic 2.13.3 |
| `export_metabase --help` / all three CLI entry points | Registered on PATH, click banners render |
| `docker compose -f infra/docker-compose.yml config --quiet` | Compose file valid |
| `make -n up down rebuild` | Targets expand correctly |

---

## Quick-reference commands

```bash
# Python
make install-dev          # editable install + dev tools
make reinstall            # clean reinstall from pyproject.toml
make test                 # run pytest

# Local Metabase stack
make up                   # http://localhost:3001 (per .env.example)
make down                 # stop (keep data)
make rebuild              # wipe DB + fresh images + up
make init-mongo           # drop & re-create the Mongo DB named by DB_NAME

# Direct pip (outside Makefile)
pip install .             # runtime
pip install -e ".[test]"  # editable + test extras only
pipx install .            # global CLI install, no venv activation
```

---

## 7. Local-dev reproduction (this session)

Extended the local stack so `import_metabase` can be run end-to-end against a fully local target, matching the production TED-SWS flow (Metabase + registered MongoDB data source → inject schema stub → Metabase API import).

### MongoDB service added to the compose stack
- `infra/docker-compose.yml` now includes a `mongo` service (image `mongo:${MONGO_VERSION:-6}`), bound to `127.0.0.1:${MONGO_HOST_PORT:-27017}`, with a `mongosh`-based healthcheck and a named `mongo-data` volume.
- Mongo runs **without authentication** — local-dev only. Any real deployment uses external AWS DocumentDB.

### Explicit bridge network
- All three services (`metabase-postgres`, `metabase`, `mongo`) are declared on an explicit `metabase-net` bridge network instead of relying on the implicit default. Behavior is equivalent but removes a class of "why can't service X reach service Y" doubts.
- Added `extra_hosts: "host.docker.internal:host-gateway"` on the `metabase` service so Metabase can reach services running directly on the Linux host if ever needed.

### Unified `.env` at the repo root
Previously two disjoint env files were loaded by two different systems. Consolidated into one.

**Before:**
- `./.env` — read by Python CLIs via `dotenv`.
- `infra/.env` — auto-loaded by compose because of file location.
- Overlap: **none** (different variable names), but awkward for a new contributor.

**After:**
- `./.env` — read by Python CLIs **and** passed to compose via `--env-file .env` in the Makefile.
- `infra/.env` and `infra/.env.example` are no longer read. Safe to delete.
- Committed template `./.env.example` merges all variables (app + infra) with local-dev defaults that match the documented walkthrough: Metabase on `3001`, Mongo on `27018`, admin `a@a.com` / `okokok123`, data source name `TEDSWS MongoDB`, database `aggregates_db`.

### Makefile additions
| Target | What it does |
|---|---|
| `make init-mongo` | Runs `tests/init_mongodb.py` to drop + re-create the Mongo DB named by `DB_NAME`. Fails fast if `./.env` is missing. |

`make up` now errors out with a clear message if `./.env` is missing, instead of silently copying a (now-removed) `infra/.env.example`.

### New helper script
- `tests/init_mongodb.py` — stand-alone script that reads `DB_AUTH_URL` and `DB_NAME` from `./.env`, drops the database if it exists, then re-creates it with a `_init_marker` collection so the database is materialized in Mongo. Idempotent.

### Code change — `METABASE_DB_NAME` is now env-overridable
- `metabase/migration/adapters/importer.py:21` changed from hardcoded `"TEDSWS MongoDB"` to `os.environ.get('METABASE_DB_NAME', default="TEDSWS MongoDB")`.
- Default behavior unchanged (still "TEDSWS MongoDB" unless explicitly overridden).
- Documented in the README's application-variables table.

### README
- New **"Running the import end-to-end locally"** section — 8-step walkthrough from `cp .env.example .env` through `import_metabase tests/test_data/export.json`.
- Environment-variables section rewritten for the single-`.env` model.
- All references to `infra/.env` / `infra/.env.example` updated or removed.

### Deletable leftovers
With the unification:
- `infra/.env` — no longer read. Delete locally.
- `infra/.env.example` — replaced by `./.env.example`. Delete from the repo.
