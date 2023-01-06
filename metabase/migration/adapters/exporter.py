from metabase.migration.model.migration_data import MigrationData
from metabase.migration.adapters.api import API
from metabase.migration.services import find_element, add_fields_to_tables
import json
from pathlib import Path
import logging

DEFAULT_EXPORT_FILE = "./data/export.json"


class Exporter:
    api: API

    def __init__(self, host: str, user: str, password: str, logger: logging.Logger):
        self.api = API(
            host=host,
            user=user,
            password=password,
        )
        self.logger = logger

    def get_collections(self):
        data_collections = []
        collections = self.api.get_collections()
        for collection in collections:
            data_collections.append(self.api.get_collection(collection["id"]))

        return data_collections

    def export_data(self) -> MigrationData:
        self.logger.info(f'Exporting Metabase ... ')
        data = MigrationData()

        self.logger.info('... collections')
        data.collections = self.get_collections()
        self.logger.info('... dashboards')
        data.dashboards = self.api.get_dashboards()
        self.logger.info('... databases')
        data.databases = self.api.get_databases()
        self.logger.info('... tables')
        data.tables = self.api.get_tables()
        add_fields_to_tables(data.tables, data.databases)

        self.logger.info('... metrics')
        data.metrics = self.api.get_metrics()
        self.logger.info('... segments')
        data.segments = self.api.get_segments()
        self.logger.info('... cards')
        data.cards = self.api.get_cards()
        self.logger.info('... permissions_groups')
        data.permissions_groups = self.api.get_permissions_groups()
        self.logger.info('... users')
        data.users = self.api.get_users()

        for dashboard in data.dashboards:
            dashboard_id = dashboard["id"]
            data.dashboard_cards.append(self.api.get_dashboard_cards(dashboard_id))

        return data

    def save_data_to_file(self, filename: str = None, data: MigrationData = None):
        if not filename:
            filename = DEFAULT_EXPORT_FILE
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if not data:
            data = self.export_data()

        self.logger.info('Saving ...')
        with open(filepath, "w+") as f:
            json.dump(data.dict(), f)
            f.close()
