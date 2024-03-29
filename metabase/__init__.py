__version__ = "0.0.1"

import os
import dotenv

dotenv.load_dotenv(verbose=True, override=True, dotenv_path="./.env")

METABASE_HOST = os.environ.get('METABASE_HOST', default=None)
METABASE_USER = os.environ.get('METABASE_USER', default=None)
METABASE_PASSWORD = os.environ.get('METABASE_PASSWORD', default=None)
DB_AUTH_URL = os.environ.get('DB_AUTH_URL', default=None)
DB_NAME = os.environ.get('DB_NAME', default=None)
