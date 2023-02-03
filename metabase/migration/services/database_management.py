import itertools
import json
import pathlib
from datetime import date

from bson import ObjectId
from pymongo import MongoClient

EXCLUDE_COLLECTION_NAMES = ["fs.chunks", "fs.files"]
COLLECTIONS_NAME_KEY = "collections"
DATABASE_NAME_KEY = "database_name"
COLLECTION_NAME_KEY = "collection_name"
PROTO_DOCUMENT_KEY = "proto_document"
MONGODB_ID_KEY = "_id"
MONGODB_ID_TYPE_KEY = "proto_id_type"
SNAPSHOT_ID_KEY = "injected_snapshot_id"
SNAPSHOT_ID_VALUE = "proto_doc"
DELETE_ME_COLLECTION = "delete_me"


def merge_dicts(source: dict, destination: dict):
    """
    """
    for key, value in source.items():
        if isinstance(value, dict):
            if (key not in destination.keys()) or (destination[key] is None):
                destination[key] = {}
            merge_dicts(value, destination[key])
        elif isinstance(value, list):
            destination[key] = []
        else:
            if key == MONGODB_ID_KEY:
                destination[key] = value
            else:
                destination[key] = None
    return destination


def create_mongodb_snapshot(database_name: str, result_snapshot_path: pathlib.Path,
                            mongodb_client: MongoClient) -> pathlib.Path:
    """

    """
    db_snapshot = {}
    collections = []
    db_snapshot[DATABASE_NAME_KEY] = database_name
    db = mongodb_client[database_name]
    collection_names = db.list_collection_names()
    for collection_name in collection_names:
        if collection_name not in EXCLUDE_COLLECTION_NAMES:
            collection = {COLLECTION_NAME_KEY: collection_name}
            db_collection = db[collection_name]
            proto_document = {}
            for document in itertools.islice(db_collection.find(), 200):
                proto_document = merge_dicts(document, proto_document)
            proto_document[MONGODB_ID_TYPE_KEY] = str(type(proto_document[MONGODB_ID_KEY]))
            proto_document[MONGODB_ID_KEY] = str(proto_document[MONGODB_ID_KEY])
            proto_document[SNAPSHOT_ID_KEY] = SNAPSHOT_ID_VALUE
            collection[PROTO_DOCUMENT_KEY] = proto_document
            collections.append(collection)
    db_snapshot[COLLECTIONS_NAME_KEY] = collections
    if result_snapshot_path.is_dir():
        result_snapshot_path = result_snapshot_path / f"{database_name}_snapshot_{date.today().isoformat()}.json"
    result_snapshot_path.write_text(data=json.dumps(db_snapshot, default=str), encoding="utf-8")
    return result_snapshot_path


def inject_mongodb_snapshot(database_snapshot_path: pathlib.Path, mongodb_client: MongoClient,
                            database_name: str = None):
    """

    """
    snapshot_content = json.loads(database_snapshot_path.read_text(encoding="utf-8"))
    database_name = database_name if database_name else snapshot_content[DATABASE_NAME_KEY]
    db = mongodb_client[database_name]
    for collection in snapshot_content[COLLECTIONS_NAME_KEY]:
        db_collection = db[collection[COLLECTION_NAME_KEY]]
        proto_document = collection[PROTO_DOCUMENT_KEY]
        if proto_document[MONGODB_ID_TYPE_KEY] == str(type(ObjectId())):
            proto_document[MONGODB_ID_KEY] = ObjectId()
        elif proto_document[MONGODB_ID_TYPE_KEY] == str(type(dict())):
            proto_document[MONGODB_ID_KEY] = {str(ObjectId()): str(ObjectId())}
        else:
            proto_document[MONGODB_ID_KEY] = str(ObjectId())
        db_collection.insert_one(document=proto_document)
    if DELETE_ME_COLLECTION in db.list_collection_names():
        db.drop_collection(DELETE_ME_COLLECTION)


def remove_mongodb_snapshot(database_name: str, mongodb_client: MongoClient):
    """

    """
    db = mongodb_client[database_name]
    collection_names = db.list_collection_names()
    for collection_name in collection_names:
        if collection_name not in EXCLUDE_COLLECTION_NAMES:
            db_collection = db[collection_name]
            db_collection.delete_many(filter={SNAPSHOT_ID_KEY: SNAPSHOT_ID_VALUE})
