import os
from pymongo import MongoClient

from metabase.migration.resources import DB_SNAPSHOT_FILE_PATH
from metabase.migration.services.database_management import create_mongodb_snapshot, inject_mongodb_snapshot, \
    remove_mongodb_snapshot
import dotenv

dotenv.load_dotenv(verbose=True, override=True)

DB_AUTH_URL = os.environ.get('DB_AUTH_URL', default=None)
DB_NAME = os.environ.get('DB_NAME', default="aggregates_db")


def test_create_mongodb_snapshot():
    mongodb_auth_url = DB_AUTH_URL
    if mongodb_auth_url:
        mongodb_client = MongoClient(mongodb_auth_url)
        create_mongodb_snapshot(database_name=DB_NAME,
                                result_snapshot_path=DB_SNAPSHOT_FILE_PATH,
                                mongodb_client=mongodb_client)


def test_inject_mongodb_snapshot():
    mongodb_auth_url = DB_AUTH_URL
    if mongodb_auth_url:
        mongodb_client = MongoClient(mongodb_auth_url)
        inject_mongodb_snapshot(database_snapshot_path=DB_SNAPSHOT_FILE_PATH, mongodb_client=mongodb_client,
                                database_name="tmp_test_database")


def test_remove_mongodb_snapshot():
    mongodb_auth_url = DB_AUTH_URL
    if mongodb_auth_url:
        mongodb_client = MongoClient(mongodb_auth_url)
        remove_mongodb_snapshot(database_name="tmp_test_database", mongodb_client=mongodb_client)
