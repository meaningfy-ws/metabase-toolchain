__version__ = "0.0.1"

import os
from pathlib import Path
import dotenv

# Search for .env in prioritised locations:
#   1. src/.env  (repo root cwd, Makefile runs from here)
#   2. .env      (cwd directly — e.g. inside src/ or a deployment dir)
#   3. walk up   (fallback: find_dotenv searches parent directories)
_env_candidates = [
    Path.cwd() / "src" / ".env",
    Path.cwd() / ".env",
]
_dotenv_path = next((p for p in _env_candidates if p.is_file()), None)

dotenv.load_dotenv(
    verbose=True,
    override=True,
    dotenv_path=str(_dotenv_path) if _dotenv_path else dotenv.find_dotenv(usecwd=True),
)

METABASE_HOST = os.environ.get("METABASE_HOST", default=None)
METABASE_USER = os.environ.get("METABASE_USER", default=None)
METABASE_PASSWORD = os.environ.get("METABASE_PASSWORD", default=None)
DB_AUTH_URL = os.environ.get("DB_AUTH_URL", default=None)
DB_NAME = os.environ.get("DB_NAME", default=None)
