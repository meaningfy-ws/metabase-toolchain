"""Create a fresh MongoDB database named by DB_NAME in ./.env.

Drops the database if it already exists, then creates it with a single
`_init_marker` collection so the database is visible to MongoDB clients
(MongoDB creates databases lazily, so a first write is needed).

Usage (from repo root):
    python tests/init_mongodb.py
"""
import os

import dotenv
from pymongo import MongoClient

dotenv.load_dotenv(dotenv_path="./.env")

DB_AUTH_URL = os.environ["DB_AUTH_URL"]
DB_NAME = os.environ["DB_NAME"]


def main() -> None:
    client = MongoClient(DB_AUTH_URL)
    if DB_NAME in client.list_database_names():
        client.drop_database(DB_NAME)
        print(f"Dropped existing database '{DB_NAME}'")
    db = client[DB_NAME]
    db["_init_marker"].insert_one({"_id": "init", "initialized": True})
    print(f"Created database '{DB_NAME}' at {DB_AUTH_URL}")
    print(f"Collections: {db.list_collection_names()}")


if __name__ == "__main__":
    main()
