install:
	@ pip install --upgrade pip
	@ pip install .

install-dev:
	@ pip install --upgrade pip
	@ pip install -e ".[dev]"

reinstall:
	@ pip uninstall -y metabase-toolchain || true
	@ pip install --upgrade --force-reinstall --no-cache-dir .

install-cli:
	@ pip install --upgrade pip
	@ pip uninstall -y metabase-toolchain || true
	@ pip install --force-reinstall --no-deps -e .
	@ echo ""
	@ echo "CLI entry points installed into $$(python -c 'import sys; print(sys.prefix)'):"
	@ for cmd in import_metabase export_metabase manage_snapshot_db; do \
		path=$$(command -v $$cmd || echo "NOT FOUND"); \
		echo "  $$cmd -> $$path"; \
	done

test:
	@ pytest tests

# =============================================================================
# Metabase local stack (docker compose)
# =============================================================================

COMPOSE = docker compose --env-file .env -f infra/docker-compose.yml -p metabase-toolchain

up:
	@ test -f .env || (echo "Error: ./.env not found at repo root. Copy .env.example to .env first." && exit 1)
	@ $(COMPOSE) up -d

down:
	@ $(COMPOSE) down

rebuild:
	@ $(COMPOSE) down -v --remove-orphans
	@ $(COMPOSE) pull
	@ $(COMPOSE) build --pull --no-cache
	@ $(COMPOSE) up -d

init-mongo:
	@ test -f .env || (echo "Error: ./.env not found at repo root. Create it first (see README)." && exit 1)
	@ python tests/init_mongodb.py

.PHONY: install install-dev reinstall install-cli test up down rebuild init-mongo
