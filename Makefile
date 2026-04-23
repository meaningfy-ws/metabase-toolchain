install:
	@ pip install --upgrade pip
	@ pip install src/.

install-dev:
	@ pip install --upgrade pip
	@ pip install -e "src/.[dev]"

reinstall:
	@ pip uninstall -y metabase-toolchain || true
	@ pip install --upgrade --force-reinstall --no-cache-dir src/.

install-cli:
	@ pip install --upgrade pip
	@ pip uninstall -y metabase-toolchain || true
	@ pip install --force-reinstall --no-deps -e src/.
	@ echo ""
	@ echo "CLI entry points installed into $$(python -c 'import sys; print(sys.prefix)'):"
	@ for cmd in import_metabase export_metabase manage_snapshot_db; do \
		path=$$(command -v $$cmd || echo "NOT FOUND"); \
		echo "  $$cmd -> $$path"; \
	done

test:
	@ pytest test

# =============================================================================
# Metabase local stack (docker compose)
# =============================================================================

COMPOSE = docker compose --env-file src/.env -f src/infra/docker-compose.yml -p metabase-toolchain

up:
	@ test -f src/.env || (echo "Error: src/.env not found. Copy src/.env.example to src/.env first." && exit 1)
	@ $(COMPOSE) up -d

down:
	@ $(COMPOSE) down

rebuild:
	@ $(COMPOSE) down -v --remove-orphans
	@ $(COMPOSE) pull
	@ $(COMPOSE) build --pull --no-cache
	@ $(COMPOSE) up -d

init-mongo:
	@ test -f src/.env || (echo "Error: src/.env not found. Create it first (see docs/README.md)." && exit 1)
	@ python test/init_mongodb.py

.PHONY: install install-dev reinstall install-cli test up down rebuild init-mongo
