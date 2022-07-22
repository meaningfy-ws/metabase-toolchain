import json
import os
from pathlib import Path
from typing import List

import dotenv

from src.migration.adapters.api import API
from src.migration.adapters.exporter import Exporter
from src.migration.model.migration_data import MigrationData

dotenv.load_dotenv(verbose=True, override=True)

MONGO_DB_USER = os.environ.get('MONGO_DB_USER')
MONGO_DB_PASS = os.environ.get('MONGO_DB_PASS')
MONGO_DB_HOST = os.environ.get('MONGO_DB_HOST')
ENV_MONGO_DB_PORT = os.environ.get('MONGO_DB_PORT')
MONGO_DB_PORT = int(ENV_MONGO_DB_PORT) if ENV_MONGO_DB_PORT else None


class Importer:
    IMPORT_FILE = Exporter.EXPORT_FILE
    api: API

    def __init__(self, host: str, user: str, password: str):
        self.api = API(
            host=host,
            user=user,
            password=password,
        )

    @classmethod
    def _import_resources(cls, items, api_call):
        for data in items:
            api_call(data)

    @classmethod
    def _update_mongodb_data(cls, database):
        if MONGO_DB_USER:
            database['details']['user'] = MONGO_DB_USER
        if MONGO_DB_PASS:
            database['details']['pass'] = MONGO_DB_PASS
        if MONGO_DB_HOST:
            database['details']['host'] = MONGO_DB_HOST
        if MONGO_DB_PORT:
            database['details']['port'] = MONGO_DB_PORT

    def _import_databases(self, databases: List):
        for database in databases:
            if database['engine'] == 'mongo':
                self._update_mongodb_data(database)
            self.api.post_database(database)

    def _import_dashboards(self, dashboards: List, dashboard_cards: List):
        for dashboard in dashboards:
            r = self.api.post_dashboard(dashboard).json()
            dashboard_id = r['id']
            dashboard_card = next(filter(lambda item: item['id'] == dashboard['id'], dashboard_cards), None)
            if dashboard_card:
                cards = dashboard_card['ordered_cards']
                for card in cards:
                    card['dashboard_id'] = dashboard_id
                    self.api.post_dashboard_card(dashboard_id, card)

    def _import_collections(self, collections: List):
        for collection in collections:
            if 'color' not in collection:
                collection['color'] = "#000000"
            self.api.post_collection(collection)

    def import_data(self, file: str = None):
        data = self.load_data(file)

        self._import_resources(data.metrics, self.api.post_metric)
        self._import_resources(data.segments, self.api.post_segment)
        self._import_resources(data.cards, self.api.post_card)
        self._import_databases(data.databases)
        self._import_collections(data.collections)
        self._import_dashboards(data.dashboards, data.dashboard_cards)

    def load_data(self, file: str = None) -> MigrationData:
        if not file:
            file = self.IMPORT_FILE
        filepath = Path(file)

        with open(filepath, "r") as f:
            data = json.load(f)
            f.close()

        return MigrationData(**data)
